import random
from pathlib import Path
from typing import Any, List
from inspect import getmembers, isfunction

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
from decoy.udf_scalar import oversample
from decoy.xeger import xeger_cached
from decoy.udf_numpy import register_numpy_random_functions

import decoy.udf_custom_functions as c_funcs


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
        register_numpy_random_functions(con)
        register_custom_udfs(con)
    return con


def register_udf_library(
    con: duckdb.DuckDBPyConnection, library, library_config, library_name: str
):
    library_functions = {k: v for k,
                         v in library_config.items() if k != "_meta"}

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


def register_custom_udfs(con: duckdb.DuckDBPyConnection) -> None:
    for func in getmembers(c_funcs, isfunction):

        fname = str(func[0])
        print(f'FNAME: {fname}')

        fargs = []
        if c_funcs.custom_config[fname]['parameters'] is not None:
            for farg in c_funcs.custom_config[fname]['parameters'].split(','):
                fargs.append(
                    getattr(ducktypes, farg.strip()))

        print(f'FARGS: {fargs}')

        rtype = getattr(ducktypes, c_funcs.custom_config[fname]["return_type"])

        print(f'RTYPE: {rtype}')

        match c_funcs.custom_config[fname]["function_type"]:
            case 'scalar':
                ftype = duckdb.functional.PythonUDFType.NATIVE
            case 'arrow':
                ftype = duckdb.functional.PythonUDFType.ARROW

        print(f'FTYPE: {ftype}')

        con.create_function(
            name=fname,
            function=func[1],
            return_type=fargs,
            parameters=rtype,
            side_effects=True,
            type=ftype,
        )


def register_udfs(con: duckdb.DuckDBPyConnection) -> None:

    con.create_function(
        name="xeger",
        function=xeger_cached,
        return_type=[ducktypes.VARCHAR],
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
