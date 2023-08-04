from numpy import random as npr
import duckdb
from duckdb import typing as ducktypes


def numpy_rand():
    return npr.rand()


def numpy_randn():
    return npr.randn()


def numpy_randint(low, high):
    return npr.randint(low, high)


def numpy_sample():
    return npr.sample()


def numpy_choice(a, p):
    """
    In order to utilise the numpy.random.choice() function, the inputs and outputs need to be formatted in a specific way. 
    Parameters:
        a (Str): a string of the choices in the format "choice1, choice2, choice3" as string will be split on commas(,)
        p (Str): a string of all the choice probabilities, the same length and format as choices. 
    Returns:
        choice (Str): A STRING of the choice from the choices list (a) based on the probability list (p)
    """
    a = a.split(",")
    p = [float(x) for x in p.split(",")]
    choice = npr.choice(a=a, p=p)
    return choice


def register_numpy_random_functions(con: duckdb.DuckDBPyConnection) -> None:

    con.create_function(
        name='numpy_rand',
        function=numpy_rand,
        return_type=None,
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_randn',
        function=numpy_rand,
        return_type=None,
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_randint',
        function=numpy_randint,
        return_type=[ducktypes.INTEGER, ducktypes.INTEGER],
        parameters=ducktypes.INTEGER,
        side_effects=True,
    )

    con.create_function(
        name='numpy_sample',
        function=numpy_sample,
        return_type=None,
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_choice',
        function=numpy_choice,
        return_type=[ducktypes.VARCHAR, ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )
