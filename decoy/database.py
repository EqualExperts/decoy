import duckdb
from duckdb import typing as ducktypes

from decoy.settings import settings
from decoy.udf_scalar import (
    get_faker_locale,
    get_mimesis_locale,
    custom_choice_generator,
)
from decoy.udf_arrow import random_shuffle, intratable_sample, oversample
from decoy.xeger import xeger_cached


def get_connection(register_funcs=True) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(settings.database_file)
    if register_funcs:
        register_udfs(con)
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
    """
    #TODO: explain why we need to cache the column again!
    """
    cache_column(table_name, column_name)

    col_ref = f"{table_name}.{column_name}"
    return random.choice(column_cache[col_ref])


def register_udfs(con: duckdb.DuckDBPyConnection) -> None:
    fkr_en = get_faker_locale("en-GB")
    mim_en = get_mimesis_locale("EN")

    con.create_function(
        name="faker_en",
        function=fkr_en,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name="mimesis_en",
        function=mim_en,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name="xeger",
        function=xeger_cached,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name="custom_choice",
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
