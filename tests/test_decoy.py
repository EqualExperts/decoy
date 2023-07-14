import pyarrow as pa
import pytest

from decoy.database import (
    custom_choice_generator,
    get_connection,
    intratable_sample,
    random_shuffle,
)

# from decoy.udf_arrow import
from decoy.settings import settings
from decoy.udf_scalar import (
    clear_column_cache,
    column_cache,
    get_column_from_cache,
    oversample,
)

settings.database_file = "test.duckdb"


def test_func(connection):
    assert True


@pytest.fixture()
def connection(request):
    print("setup")

    def teardown():
        print("teardown")

    request.addfinalizer(teardown)

    return get_connection()


def test_cache_column(connection):
    connection.execute(
        """
    CREATE OR REPLACE TABLE test_cached_column AS SELECT range from range(10)
    """
    )
    get_column_from_cache("test_cached_column", "range")
    assert len(column_cache["test_cached_column.range"]) == 10


def test_custom_choice_generator(connection):
    test_choice = custom_choice_generator()
    assert test_choice in ["Fake 1", "Fake 2", "Fake 3"]


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
