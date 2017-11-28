from contextlib import contextmanager
import re
import threading


def pseudo_tuple(name, fields):
    if not re.match('^[_a-zA-Z][_a-zA-Z0-9]*$', name):
        raise ValueError(f"name must be a legal identifier: {name}")

    if len(fields) != len(set(fields)):
        raise ValueError("all fields must be distinct")

    for field in fields:
        if not re.match('^[a-zA-Z][_a-zA-Z0-9]*$', name):
            raise ValueError(f"name must be a legal identifier and not start with an underscore: {name}")

    def __init__(self, *args, **kwargs):
        if len(args) > len(fields):
            raise ValueError(f"extra positional args: {args[len(fields):]}")
        for field, arg in zip(fields, args):
            if field in kwargs:
                raise ValueError(f"argument duplicated in kwargs: {field}")
            kwargs[field] = arg
        for field in fields[len(args):]:
            if field not in kwargs:
                kwargs[field] = None
        self.__dict__.update(**kwargs)

    def __iter__(self):
        return (self.__dict__[field] for field in fields)

    def __str__(self):
        pos_items = [(k, self.__dict__[k]) for k in fields]
        kw_items = [(k, v) for k, v in self.__dict__.items() if k not in fields]
        args = ', '.join(f"{k}={v}" for k, v in pos_items + kw_items)
        return f"{name}({args})"

    def __repr__(self):
        pos_items = [(k, self.__dict__[k]) for k in fields]
        kw_items = [(k, v) for k, v in self.__dict__.items() if k not in fields]
        args = ', '.join(f"{k}={v!r}" for k, v in pos_items + kw_items)
        return f"{name}({args})"

    return type(name, (), {
        '__init__': __init__,
        '__iter__': __iter__,
        '__str__': __str__,
        '__repr__': __repr__,
    })


def lines(str):
    yield from str.splitlines()


def printlines(lines, end='\n', file=None):
    for line in lines:
        print(line, end=end, file=file)


def print_to(file, mode="w"):
    def decorator(fn):
        with open(file, mode) as f:
            printlines(fn(), file=f)
    return decorator
