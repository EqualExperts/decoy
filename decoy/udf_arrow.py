from mimesis import Generic, Locale
import pandas as pd
import pyarrow as pa
import random
from typing import Any


def random_shuffle(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)


def intratable_sample(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, replace=True, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)
