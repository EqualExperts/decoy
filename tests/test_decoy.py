import pytest

from decoy.database import settings, column_cache, get_connection, cache_column

settings["database_file"] = 'test.duckdb'


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
    connection.execute('''
    CREATE TABLE IF NOT EXISTS test_cache_column AS SELECT range from range(10)
    ''')
    cache_column('test_cache_column', 'range')
    assert len(column_cache['test_cache_column.range']) == 10
