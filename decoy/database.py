import duckdb
from duckdb import typing as ducktypes

from decoy.settings import settings
from decoy.udf_scalar import (
    get_faker_locale,
    get_mimesis_locale,
    custom_choice_generator,
    np_rand,
    pyrandom
)
from decoy.udf_arrow import random_shuffle, intratable_sample, oversample
from decoy.xeger import xeger_cached


def get_connection(register_funcs=True) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(settings.database_file)
    if register_funcs:
        register_udfs(con)
    return con


def register_udfs(con: duckdb.DuckDBPyConnection) -> None:
    fkr_en = get_faker_locale("en-GB")
    mim_en = get_mimesis_locale("EN")
    npr = np_rand()
    pyr = pyrandom()

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
        name="np_rand",
        function=npr,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name="pyrandom",
        function=pyr,
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
