import random
from pathlib import Path
from typing import Any, List

import duckdb
import yaml
from duckdb import typing as ducktypes
from faker import Faker
from mimesis import Generic, Locale

from decoy.settings import settings
from decoy.udf_arrow import (
    intratable_sample,
    messy_data_junkadder,
    messy_data_nullifier,
    random_shuffle,
)
from decoy.udf_scalar import custom_choice_generator, oversample
from decoy.xeger import xeger_cached


def getattr_submodule(mod: Any, fpath: str):
    fpaths = fpath.split(".")
    attr = mod
    for att in fpaths:
        attr = getattr(attr, att)

    return attr


def getattr_submodule_noargs(mod: Any, fpath: str):
    attr = getattr_submodule(mod, fpath)

    def noargs():
        return attr()

    return noargs


def get_connection(register_funcs=True) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(settings.database_file)
    if register_funcs:
        register_udfs(con)
        register_udfs_from_config(con)
    return con


def register_udf_library(
    con: duckdb.DuckDBPyConnection, library, library_config, library_name: str
):
    library_functions = {k: v for k, v in library_config.items() if k != "_meta"}

    for fname, fconfig in library_functions.items():
        rtype = getattr(ducktypes, fconfig["return_type"])
        fargs = []

        for arg in fconfig["arguments"]:
            if type(arg["type"]) is list:
                fargs.append([getattr(ducktypes, arg["type"][0])])
            else:
                fargs.append(getattr(ducktypes, arg["type"]))

        function_name = f"{library_name}_{fname.replace('.', '_')}"

        match fconfig["dispatch"]:
            case "native":
                con.create_function(
                    name=function_name,
                    function=getattr_submodule(library, fname),
                    return_type=fargs,
                    parameters=rtype,
                    side_effects=True,
                )
            case "no_arg":
                con.create_function(
                    name=function_name,
                    function=getattr_submodule_noargs(library, fname),
                    return_type=[],
                    parameters=rtype,
                    side_effects=True,
                )
            case default:
                print(f"Dispatch type {fconfig['dispatch']} not found.")


def register_udfs_from_config(con: duckdb.DuckDBPyConnection) -> None:
    fkr_en = Faker("en-GB")
    mim_en = Generic(Locale.EN)

    with open(Path(__file__).parent / "udfspec.yml", "r") as f:
        config = yaml.safe_load(f)

        register_udf_library(con, fkr_en, config["faker_en"], "faker")
        register_udf_library(con, mim_en, config["mimesis_en"], "mimesis")
        register_udf_library(con, random, config["random"], "random")


def register_udfs(con: duckdb.DuckDBPyConnection) -> None:
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
        name="messy_data_nullifier",
        function=messy_data_nullifier,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
        type=duckdb.functional.PythonUDFType.ARROW,
    )

    con.create_function(
        name="messy_data_junkadder",
        function=messy_data_junkadder,
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
