import random
import re

column_cache = {}

IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_.]*$')


def _validate_identifier(name: str) -> str:
    if not IDENTIFIER_PATTERN.match(name):
        raise ValueError(f"Invalid identifier: {name}")
    return name


def get_column_from_cache(table_name: str, column_name: str) -> None:
    validated_table = _validate_identifier(table_name)
    validated_column = _validate_identifier(column_name)

    cache_key = f"{validated_table}.{validated_column}"
    if cache_key not in column_cache:
        from decoy.database import get_connection

        con = get_connection(False)
        con.execute(f"SELECT {validated_column} FROM {validated_table}")
        column_cache[cache_key] = [val[0] for val in con.fetchall()]

    return column_cache[cache_key]


def clear_column_cache(key_name: str = None):
    """If a connection oversamples an updated table that was
    previously oversampled it will return the old cached values.

    This function should be run before every query to reset the
    cache to prevent it."""
    if key_name is None:
        for k in list(column_cache.keys()):
            del column_cache[k]
    else:
        del column_cache[key_name]


def oversample(table_name: str, column_name: str) -> str:
    """
    Call clear_column_cache on every query if possible to
    prevent returning stale values
    """
    col = get_column_from_cache(table_name, column_name)

    col_ref = f"{table_name}.{column_name}"
    return random.choice(column_cache[col_ref])
