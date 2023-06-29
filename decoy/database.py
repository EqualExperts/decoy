import duckdb
from duckdb import typing as ducktypes
from faker import Faker
from typing import Callable, Any
import pandas as pd
import pyarrow as pa
import random

settings = {"database_file": "decoy.duckdb"}
column_cache = {}


def get_connection(register_funcs=True) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(settings["database_file"])
    if register_funcs:
        register_en(con)
    return con


def cache_column(table_name: str, column_name: str) -> None:
    con = get_connection(False)
    con.execute(f"SELECT {column_name} FROM {table_name}")
    column_cache[f"{table_name}.{column_name}"] = [val[0]
                                                   for val in con.fetchall()]


def get_faker_locale(locale: str) -> Callable[[str], Any]:
    fkr = Faker(locale)

    def dispatch(fname: str):
        return getattr(fkr, fname)()

    return dispatch


def custom_choice_generator() -> ducktypes.VARCHAR:
    return random.choice(["Fake 1", "Fake 2", "Fake 3"])


def random_shuffle(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)


def intratable_sample(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, replace=True, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)


def oversample(table_name: str, column_name: str) -> str:
    cache_column(table_name, column_name)

    col_ref = f"{table_name}.{column_name}"
    return random.choice(column_cache[col_ref])


def register_en(con: duckdb.DuckDBPyConnection) -> None:

    fkr_en = get_faker_locale("en-GB")

    con.create_function(
        name="faker_init_en",
        function=fkr_en,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name="choice",
        function=custom_choice_generator,
        return_type=[],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name="shuffle",
        function=random_shuffle,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
        type=duckdb.functional.PythonUDFType.ARROW,
    )

    con.create_function(
        name="intratable_sample",
        function=intratable_sample,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
        type=duckdb.functional.PythonUDFType.ARROW,
    )

    con.create_function(
        name="oversample",
        function=oversample,
        return_type=[ducktypes.VARCHAR, ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )
