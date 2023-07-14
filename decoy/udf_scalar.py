import random
from typing import Any, Callable

from duckdb import typing as ducktypes
from faker import Faker
from mimesis import Generic, Locale
from numpy import random as npr

column_cache = {}


def get_faker_locale(locale: str) -> Callable[[str], Any]:
    fkr = Faker(locale)

    def dispatch(fname: str):
        return getattr(fkr, fname)()

    return dispatch


def get_mimesis_locale(locale: str) -> Callable[[str], Any]:
    loc = getattr(Locale, locale)
    mim = Generic(loc)

    def dispatch(fname: str):
        fnames = fname.split(".")
        generator = mim
        for att in fnames:
            generator = getattr(generator, att)

        return generator()

    return dispatch


def np_rand():
    def dispatch(fname: str):
        return getattr(npr, fname)()

    return dispatch


def pyrandom():
    def dispatch(fname: str):
        return getattr(random, fname)()

    return dispatch


def get_column_from_cache(table_name: str, column_name: str) -> None:
    cache_key = f"{table_name}.{column_name}"
    if cache_key not in column_cache:
        from decoy.database import get_connection

        con = get_connection(False)
        con.execute(f"SELECT {column_name} FROM {table_name}")
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


def custom_choice_generator() -> ducktypes.VARCHAR:
    return random.choice(["Fake 1", "Fake 2", "Fake 3"])
