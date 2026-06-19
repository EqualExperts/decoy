'''
This script is where you can add your own custom generators. 

They will be imported into Decoy as the function name you choose.

Please note: At present Duckdb register UDFs has parameters and return_types reversed. We have it the correct way round.

'''
import random
import pyarrow as pa
import pandas as pd

from duckdb import typing as ducktypes
from typing import Any, Callable


custom_config = {
    'demo_scalar_choice':
        {'function_type': 'scalar',
         # Usually you will put this in [] eg. [VARCHAR]. Separate multiple values with commas (,)
         'parameters': None,
         'return_type': 'VARCHAR'
         },

    'demo_arrow_doubler':
        {'function_type': 'arrow',
         'parameters': 'VARCHAR',
         'return_type': 'VARCHAR'},

}


def demo_scalar_choice() -> ducktypes.VARCHAR:
    '''
    The Scalar functions return single values and are run on a rowwise loop.
    '''
    return random.choice(["Fake 1", "Fake 2", "Fake 3"])


def demo_arrow_doubler(x: list[list[Any]]) -> pa.Table:
    '''
    The arrow functions take lists and inputs and output lists too.
    However the input and output length must be equal!!
    '''
    df = pd.DataFrame(x.to_pandas())
    shuffled = df * 2
    return pa.lib.Table.from_pandas(shuffled)
