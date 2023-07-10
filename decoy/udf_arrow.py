from mimesis import Generic, Locale
import pandas as pd
import pyarrow as pa
import numpy as np
import random
from typing import Any

junkadder_settings = {"options": ['A', 'B', 'C', 'D'],
                      "probabilities": [0.4, 0.2, 0.3, 0.1]}


def random_shuffle(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)


def intratable_sample(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    shuffled = df.sample(frac=1, replace=True, ignore_index=True)
    return pa.lib.Table.from_pandas(shuffled)


def messy_data_nullifier(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    df['col2'] = df.sample(frac=0.7)
    sampled = pd.DataFrame(df['col2'])
    return pa.lib.Table.from_pandas(sampled)


def messy_data_junkadder(x: list[list[Any]]) -> pa.Table:
    df = pd.DataFrame(x.to_pandas())
    col = df['c0']
    number_of_swaps = int(np.ceil(len(col)*0.3))
    choices = np.random.choice(
        a=junkadder_settings['options'],
        size=number_of_swaps,
        p=junkadder_settings['probabilities'])
    col.iloc[np.random.randint(0, len(col), number_of_swaps)] = choices
    return pa.lib.Table.from_pandas(pd.DataFrame(col))
