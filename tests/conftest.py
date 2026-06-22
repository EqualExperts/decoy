import pytest
from decoy.database import get_connection
from decoy.settings import settings


@pytest.fixture()
def connection(tmp_path):
    db_file = tmp_path / "test.duckdb"
    settings.database_file = str(db_file)
    con = get_connection()
    yield con
    con.close()
    if db_file.exists():
        db_file.unlink()