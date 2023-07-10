from duckdb import typing as ducktypes
from faker import Faker
from mimesis import Generic, Locale
import random
from typing import Callable, Any
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


def cache_column(table_name: str, column_name: str) -> None:
    cache_key = f"{table_name}.{column_name}"
    if cache_key not in column_cache:
        from decoy.database import get_connection

        con = get_connection(False)
        con.execute(f"SELECT {column_name} FROM {table_name}")
        column_cache[cache_key] = [val[0] for val in con.fetchall()]


def oversample(table_name: str, column_name: str) -> str:
    """
    #TODO: explain why we need to cache the column again!
    """
    cache_column(table_name, column_name)

    col_ref = f"{table_name}.{column_name}"
    return random.choice(column_cache[col_ref])


def custom_choice_generator() -> ducktypes.VARCHAR:
    return random.choice(["Fake 1", "Fake 2", "Fake 3"])
