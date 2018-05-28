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


def print_to(file, mode='w'):
    def decorator(fn):
        with open(file, mode) as f:
            printlines(fn(), file=f)
    return decorator


def generate(file):
    def decorator(fn):
        sections = {}
        try:
            f = open(file)
        except FileNotFoundError:
            pass
        else:
            with f:
                open_section = None
                for i, line in enumerate(f, start=1):
                    m = re.search(r'<(/)?GSL customizable: (.+)>', line)
                    if m:
                        if m.group(1):
                            if not open_section:
                                raise ValueError(f"Line {i} (old): closing unopened customizable '{m.group(2)}'")
                            elif m.group(2) != open_section:
                                raise ValueError(f"Line {i} (old): closing unopened customizable '{m.group(2)}'"
                                                 f" (open customizable is '{open_section}')")
                            open_section = None
                        else:
                            if open_section:
                                raise ValueError(f"Line {i} (old): nested customizable '{m.group(2)}'")
                            open_section = m.group(2)
                            if open_section in sections:
                                raise ValueError(f"Line {i} (old): duplicate customizable '{open_section}'")
                            sections[open_section] = []
                    elif open_section:
                        sections[open_section].append(line.rstrip('\r\n'))
                if open_section:
                    raise ValueError(f"Line {i} (old): unclosed customizable '{open_section}'")

        @print_to(file)
        def code():
            open_section = None
            new_sections = set()
            skip = False
            for i, line in enumerate(fn(), start=1):
                m = re.search(r'<(/)?GSL customizable: (.+)>', line)
                if m:
                    yield line
                    if m.group(1):
                        if not open_section:
                            raise ValueError(f"Line {i} (new): closing unopened customizable '{m.group(2)}'")
                        elif m.group(2) != open_section:
                            raise ValueError(f"Line {i} (new): closing unopened customizable '{m.group(2)}'"
                                             f" (open customizable is '{open_section}')")
                        open_section = None
                        skip = False
                    else:
                        if open_section:
                            raise ValueError(f"Line {i} (new): nested customizable '{m.group(2)}'")
                        open_section = m.group(2)
                        if open_section in new_sections:
                            raise ValueError(f"Line {i} (new): duplicate customizable '{open_section}'")
                        new_sections.add(open_section)
                        skip = open_section in sections
                        if skip:
                            yield from sections[open_section]
                elif not skip:
                    yield line
            if open_section:
                raise ValueError(f"Line {i} (new): unclosed customizable '{open_section}'")

    return decorator
