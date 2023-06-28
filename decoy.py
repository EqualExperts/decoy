import duckdb
from duckdb import typing as ducktypes
from faker import Faker
from typing import Callable, Any
import pandas as pd
import pyarrow as pa
import random

# global_con = duckdb.connect("test.duckdb")

cached_column = []


def cache_column(table_name, column_name):
    global cached_column
    con = duckdb.connect("test.duckdb")
    con.execute(f"SELECT {column_name} FROM {table_name}")
    cached_column = [val[0] for val in con.fetchall()]


def get_from_cache():
    return random.choice(cached_column)


def get_faker_locale(locale: str) -> Callable[[str], Any]:
    fkr = Faker(locale)

    def dispatch(fname: str):
        return getattr(fkr, fname)()

    return dispatch


def custom_choice_generator() -> ducktypes.VARCHAR:
    return random.choice(["Fake 1", "Fake 2", "Fake 3"])


def random_shuffle(x):
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)


def intratable_sample(x):
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, replace=True, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)


def oversample(table_name, column_name):
    # global_con.execute(
    #     f"SELECT {column_name} FROM {table_name} ORDER BY RANDOM() LIMIT 1"
    # )
    # return global_con.fetchone()[0]

    if not len(cached_column):
        cache_column(table_name, column_name)

    return get_from_cache()


def register_en(con: duckdb.DuckDBPyConnection) -> None:
    fkr_en = get_faker_locale("en-GB")
    con.create_function(
        name="decoy_en",
        function=fkr_en,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )
    con.create_function(
        name="decoy_choice",
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
