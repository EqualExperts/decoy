from mimesis import Generic, Locale
import pandas as pd
import pyarrow as pa
import random
from typing import Any

column_cache = {}


def cache_column(table_name: str, column_name: str) -> None:
    cache_key = f"{table_name}.{column_name}"
    if cache_key not in column_cache:
        from decoy.database import get_connection

        con = get_connection(False)
        con.execute(f"SELECT {column_name} FROM {table_name}")
        column_cache[cache_key] = [val[0] for val in con.fetchall()]


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
