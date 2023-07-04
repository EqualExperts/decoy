import duckdb
import pandas as pd
from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import PlPgsqlLexer

exception_list = (
    duckdb.ParserException,
    duckdb.CatalogException,
    duckdb.BinderException,
)


def print_rows(rows: pd.DataFrame) -> None:
    print("----------")
    print(rows.head(50))


def repl(con: duckdb.DuckDBPyConnection) -> None:
    fh = FileHistory(".repl_history")
    s = PromptSession(
        message="> ",
        enable_history_search=True,
        history=fh,
        lexer=PygmentsLexer(PlPgsqlLexer),
        multiline=True,
    )
    print(
        "Enter SQL commands to execute against the DB. <esc><enter> or <alt/opt><enter> to submit."
    )
    while True:
        text = s.prompt()

        try:
            con.execute(text)
        except exception_list as e:
            """
            ParserException == 'sel'
            CatalogException == 'select * from nonexisting'
            BinderException == select * from duckdb_functions() WHERE function_name = oversample;
            """
            print_formatted_text(HTML(f"<ansired>{e}</ansired>"))
            continue

        try:
            res = con.fetch_df()
        except duckdb.InvalidInputException as e:
            print("No results")
            continue
        print_rows(res)
