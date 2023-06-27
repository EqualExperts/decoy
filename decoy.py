import duckdb
from duckdb import typing as ducktypes
from faker import Faker
from typing import Callable, Any
import random


def get_faker_locale(locale: str) -> Callable[[str], Any]:
    fkr = Faker(locale)

    def dispatch(fname: str):
        return getattr(fkr, fname)()

    return dispatch


def custom_choice_generator():
    return random.choice(["Fake 1", "Fake 2", "Fake 3"])


def register_en(con: duckdb.DuckDBPyConnection) -> None:
    fkr_en = get_faker_locale("en-GB")
    con.create_function(
        "decoy_en", fkr_en, [ducktypes.VARCHAR], ducktypes.VARCHAR, side_effects=True
    )
    con.create_function(
        "decoy_choice",
        custom_choice_generator,
        [],
        ducktypes.VARCHAR,
        side_effects=True,
    )
