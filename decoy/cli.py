#!/usr/bin/env python3
import os
import sys
from io import TextIOWrapper

import click
import duckdb
import jupyter_client
from prompt_toolkit import HTML, print_formatted_text

from decoy.cli_io import print_rows, repl
from decoy.database import get_connection
from decoy.schema_parse import parse_full_sql_schema
from decoy.settings import settings


@click.group()
def rootcmd():
    pass


@rootcmd.command()
def kernel_install():
    from ipykernel.kernelspec import install
    from jupyter_client.kernelspec import install_kernel_spec

    spec = jupyter_client.kernelspec.KernelSpec(
        argv=[sys.executable, "-m", "decoy.kernel", "-f", "{connection_file}"],
        env={"VIRTUAL_ENV": os.getenv("VIRTUAL_ENV")},
        language="sql",
        display_name="Decoy",
    )
    with open("decoy/kernel.json", "w") as f:
        f.write(spec.to_json())

    install_path = jupyter_client.kernelspec.install_kernel_spec(
        "decoy", kernel_name="decoy", user=True, replace=True
    )
    print(f"Decoy kernel installed at {install_path}")


@rootcmd.command()
@click.argument("filename", type=click.File("r"))
@click.option("-d", "--database", "database")
def exec(filename: TextIOWrapper, database=None):
    """Executes the sql in <filename> against duckdb.
    Operations can be separated with ---"""
    if database:
        settings.database_file = database

    con = get_connection()

    input_sql_list = filename.read().split("---")
    for input_sql in input_sql_list:
        try:
            con.execute(input_sql)
        except duckdb.ParserException as pe:
            print_formatted_text(HTML(f"<ansired>{pe}</ansired>"))
            sys.exit(1)
        res = con.fetchdf()
        print_rows(res)


@rootcmd.command(name="repl")
@click.option("-d", "--database", "database")
def repl_commmand(database):
    """Starts a REPL to execute SQL with faker and custom generation functions registered."""
    if database:
        settings.database_file = database

    con = get_connection()
    repl(con)


@rootcmd.command(name="sqlparse")
@click.argument("inputfilename", type=str)
@click.argument("outputfilename", type=str)
@click.argument("nrows", type=int)
def parse_sql_schema(inputfilename, outputfilename, nrows):
    con = get_connection()
    parse_full_sql_schema(inputfilename, outputfilename, nrows)


if __name__ == "__main__":
    rootcmd()
