import duckdb
import tempfile

import pyarrow as pa
import pytest

from decoy.database import (
    intratable_sample,
    random_shuffle,
)
from decoy.UDF.udf_scalar import (
    clear_column_cache,
    column_cache,
    get_column_from_cache,
    oversample,
)


def test_func(connection):
    assert True


def test_cache_column(connection):
    connection.execute(
        """
    CREATE OR REPLACE TABLE test_cached_column AS SELECT range from range(10)
    """
    )
    get_column_from_cache("test_cached_column", "range")
    assert len(column_cache["test_cached_column.range"]) == 10


def test_random_shuffle(connection):
    """
    I didn't feel like testing the pandas shuffle function was needed.
    Instead the purpose is making sure the input shape matches the output shape.
    This is to ensure compatibility with the PyArrow functionality of DuckDB
    """
    test_input = pa.array(["A", "B", "C", "D", "E"])
    test_output = random_shuffle(test_input)
    assert len(test_input) == len(test_output)


def test_intratable_sample(connection):
    test_input = pa.array(["A", "B", "C", "D", "E"])
    test_output = intratable_sample(test_input)
    assert len(test_input) == len(test_output)


def test_oversample(connection):
    assert oversample("test_cached_column", "range") in range(10)


def test_sql_oversample(connection):
    # create some data and oversample it
    connection.execute(
        """CREATE OR REPLACE table test_oversample AS (SELECT range, faker_name() as name FROM range(10));"""
    )
    connection.execute("SELECT * FROM test_oversample;")
    res = [r[1] for r in connection.fetchall()]
    connection.execute(
        """SELECT oversample('test_oversample', 'name') FROM range(20);"""
    )
    # make sure all of our oversampled data exists in the original data
    res_sampled = [r[0] for r in connection.fetchall()]
    for row in res_sampled:
        assert row in res


def test_sql_oversample_cached_table_change(connection):
    # create some data and oversample it
    connection.execute(
        """CREATE OR REPLACE table test_oversample2 AS (SELECT range, faker_name() as name FROM range(10));"""
    )
    connection.execute("SELECT * FROM test_oversample2;")
    original_res = [r[1] for r in connection.fetchall()]
    connection.execute(
        """SELECT oversample('test_oversample2', 'name') FROM range(20);"""
    )
    # make sure all of our oversampled data exists in the original data
    res_sampled = [r[0] for r in connection.fetchall()]
    for row in res_sampled:
        assert row in original_res

    # replace with new values
    connection.execute(
        """CREATE OR REPLACE table test_oversample2 AS (SELECT range, faker_name() as name FROM range(10));"""
    )
    clear_column_cache()
    connection.execute(
        """SELECT oversample('test_oversample2', 'name') FROM range(20);"""
    )
    res_oversampled_cached = [r[0] for r in connection.fetchall()]
    for row in res_oversampled_cached:
        assert row not in original_res


def test_local_filesystem_blocked(connection):
    """File read operations should be blocked by enable_external_access setting."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=True) as f:
        f.write("col1,col2\n1,2\n3,4")
        f.flush()

        with pytest.raises(duckdb.PermissionException) as exc_info:
            connection.execute(f"SELECT * FROM read_csv_auto('{f.name}')")
        assert "file system operations are disabled" in str(exc_info.value)
