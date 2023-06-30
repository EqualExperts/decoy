import duckdb
import pandas as pd
from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.history import FileHistory

exception_list = (
    duckdb.ParserException,
    duckdb.CatalogException,
    duckdb.BinderException,
)


def print_rows(rows: pd.DataFrame) -> None:
    print("----------")
    print(rows.head(10))


def repl(con: duckdb.DuckDBPyConnection) -> None:
    fh = FileHistory(".repl_history")
    s = PromptSession(message="sql: ", enable_history_search=True, history=fh)
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

        res = con.fetch_df()
        print_rows(res)
