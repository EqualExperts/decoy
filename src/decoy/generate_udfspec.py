import inspect
import random
from datetime import date, datetime, time

import faker
import mimesis
import numpy
import yaml

allowed_return_types = [str, int, time, date, datetime, float, None]

type_mapping = {
    str: "VARCHAR",
    int: "INTEGER",
    float: "FLOAT",
    date: "DATE",
    datetime: "TIMESTAMP",
    time: "TIME",
    None: "SQLNULL",
}
deny_list = ["seed", "parse", "lexify", "pystr_format", "setstate"]


def get_lib_spec(lib):
    collected = {"_meta": {"arg_type": "basic"}}
    for fname in dir(lib):
        if (
            not fname.startswith("__")
            and not fname.startswith("_")
            and fname not in deny_list
        ):
            f = getattr(lib, fname)
            if inspect.isfunction(f) or inspect.ismethod(f):
                sig = inspect.signature(f)
                ra = str
                args = []
                for pname, pann in sig.parameters.items():
                    args.append(
                        {
                            "name": pname,
                            "default": str(pann.default)
                            if not inspect._empty
                            else None,
                            "kind": str(pann.kind),
                        }
                    )

                    collected[fname] = {
                        "dispatch": "native",
                        "arguments": args,
                        "return_type": type_mapping[ra],
                    }

    return collected


def get_lib_spec_annotated(lib, prefix=None, include_args=True):
    collected = {"_meta": {"arg_type": "annotated"}}
    for fname in dir(lib):
        if (
            not fname.startswith("__")
            and not fname.startswith("_")
            and fname not in deny_list
        ):
            f = getattr(lib, fname)

            if inspect.isfunction(f) or inspect.ismethod(f):
                sig = inspect.signature(f)
                ra = sig.return_annotation
                if ra in allowed_return_types:
                    args = []
                    dispatch = "native" if include_args else "no_arg"

                    if include_args:
                        for pname, pann in sig.parameters.items():
                            if pann.default is inspect._empty:
                                deflt = None
                            else:
                                deflt = str(pann.annotation)
                            args.append(
                                {
                                    "name": pname,
                                    "type": type_mapping.get(
                                        pann.annotation, str(pann.annotation)
                                    ),
                                    "default": deflt,
                                    "kind": str(pann.kind),
                                }
                            )

                    if prefix:
                        collected[f"{prefix}.{fname}"] = {
                            "dispatch": dispatch,
                            "arguments": args,
                            "return_type": type_mapping.get(ra, str(ra)),
                        }
                    else:
                        collected[fname] = {
                            "dispatch": dispatch,
                            "arguments": args,
                            "return_type": type_mapping.get(ra, str(ra)),
                        }
            else:
                if prefix is None:
                    submodule = get_lib_spec_annotated(f, fname, include_args)
                    collected.update(submodule)
                    continue

    return collected


if __name__ == "__main__":
    faker_spec_args = get_lib_spec_annotated(faker.Faker("en-GB"), None, True)
    mimesis_spec_args = get_lib_spec_annotated(
        mimesis.Generic(mimesis.Locale.EN), None, True
    )
    faker_spec_noargs = get_lib_spec_annotated(
        faker.Faker("en-GB"), None, False)
    mimesis_spec_noargs = get_lib_spec_annotated(
        mimesis.Generic(mimesis.Locale.EN), None, False
    )
    random_spec = get_lib_spec(random)
    numpy_spec = get_lib_spec(
        numpy.random
    )  # numpy can't be introspected due to it being all compiled as builtin

    libs_args = {
        "faker_en": faker_spec_args,
        "mimesis_en": mimesis_spec_args,
        "random": random_spec,
        "numpy": numpy_spec,
    }

    with open("ref_udfspec_full_args.yml", "w") as f:
        f.write(yaml.safe_dump(libs_args))

    libs_noargs = {
        "faker_en": faker_spec_noargs,
        "mimesis_en": mimesis_spec_noargs,
        "random": random_spec,
        "numpy": numpy_spec,
    }

    with open("ref_udfspec_no_args.yml", "w") as f:
        f.write(yaml.safe_dump(libs_noargs))
