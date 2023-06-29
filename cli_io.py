import duckdb
import pandas as pd
from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.history import FileHistory


def print_rows(rows: pd.DataFrame):
    print(rows.head(10))


def repl(con):
    fh = FileHistory(".repl_history")
    s = PromptSession(message="sql: ", enable_history_search=True, history=fh)
    while True:
        text = s.prompt()

        try:
            con.execute(text)
        except duckdb.ParserException as pe:
            print_formatted_text(HTML(f"<ansired>{pe}</ansired>"))
            continue

        res = con.fetch_df()
        print_rows(res)
