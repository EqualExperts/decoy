from datetime import time, date, datetime
import faker
import inspect
import mimesis
import numpy
import random
import yaml

allowed_return_types = [str, int, time, date, datetime, float, None]
allowed_arg_types = [str, int, time, datetime, None]

type_mapping = {
    str: "VARCHAR",
    int: "INTEGER",
    float: "FLOAT8",
    date: "DATE",
    datetime: "TIMESTAMP",
    time: "TIME",
    None: None,
}
deny_list = ["seed"]


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
                            "default": str(pann.default if not inspect._empty else ""),
                            "kind": str(pann.kind),
                        }
                    )

                    collected[fname] = {
                        "arguments": args,
                        "return_type": type_mapping[ra],
                    }

    return collected


def get_lib_spec_annotated(lib, prefix=None):
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
                    disallowed = False
                    for pname, pann in sig.parameters.items():
                        if pann.annotation not in allowed_arg_types:
                            disallowed = True
                            break

                        args.append(
                            {
                                "name": pname,
                                "type": type_mapping[pann.annotation],
                                "default": str(pann.default),
                                "kind": str(pann.kind),
                            }
                        )
                    if disallowed:
                        continue

                    if prefix:
                        collected[f"{prefix}.{fname}"] = {
                            "arguments": args,
                            "return_type": type_mapping[ra],
                        }
                    else:
                        collected[fname] = {
                            "arguments": args,
                            "return_type": type_mapping[ra],
                        }
            else:
                if prefix is None:
                    submodule = get_lib_spec_annotated(f, fname)
                    collected.update(submodule)
                    continue

    return collected


if __name__ == "__main__":
    faker_spec = get_lib_spec_annotated(faker.Faker("en-GB"))
    mimesis_spec = get_lib_spec_annotated(mimesis.Generic(mimesis.Locale.EN))
    random_spec = get_lib_spec(random)
    numpy_spec = get_lib_spec(numpy.random)

    libs = {
        "faker_en": faker_spec,
        "mimesis_en": mimesis_spec,
        "random": random_spec,
        "numpy": numpy_spec,
    }

    with open("udfspec.yml", "w") as f:
        f.write(yaml.safe_dump(libs))
