from duckdb import typing as ducktypes
from faker import Faker
from mimesis import Generic, Locale
import random
from typing import Callable, Any
from numpy import random as npr


def get_faker_locale(locale: str) -> Callable[[str], Any]:
    fkr = Faker(locale)

    def dispatch(fname: str):
        return getattr(fkr, fname)()

    return dispatch


def get_mimesis_locale(locale: str) -> Callable[[str], Any]:
    loc = getattr(Locale, locale)
    mim = Generic(loc)

    def dispatch(fname: str):
        fnames = fname.split(".")
        generator = mim
        for att in fnames:
            generator = getattr(generator, att)

        return generator()

    return dispatch

def np_rand():
    def dispatch(fname:str):
        return getattr(npr, fname)()
    
    return dispatch


def custom_choice_generator() -> ducktypes.VARCHAR:
    return random.choice(["Fake 1", "Fake 2", "Fake 3"])
