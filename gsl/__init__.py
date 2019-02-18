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
    EMPTY, OPEN, CLOSE = 'empty', 'open', 'close'

    def marker_match(line):
        return re.search(r'<(default )?GSL customizable: ([-\w]+)( /)?>|</GSL customizable: ([-\w]+)>', line)

    def marker_info(m):
        default = m.group(1) is not None
        opening = m.group(2) is not None
        self_closing = m.group(3) is not None
        name = m.group(2) if opening else m.group(4)

        return name, EMPTY if self_closing else OPEN if opening else CLOSE, default if opening else None

    def marker_format(m, name, mode, default):
        prefix = '/' if mode == CLOSE else 'default ' if default else ''
        suffix = ' /' if mode == EMPTY else ''
        return f'{m.string[:m.start()]}<{prefix}GSL customizable: {name}{suffix}>{m.string[m.end():]}'

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
                    m = marker_match(line)
                    if m:
                        name, mode, default = marker_info(m)
                        if mode == CLOSE:
                            if not open_section:
                                raise ValueError(f"Line {i} (old): closing unopened customizable '{name}'")
                            elif name != open_section:
                                raise ValueError(f"Line {i} (old): closing unopened customizable '{name}'"
                                                 f" (open customizable is '{open_section}')")

                            open_section = None
                        elif mode == OPEN:
                            if open_section:
                                raise ValueError(f"Line {i} (old): nested customizable '{name}'")
                            if name in sections:
                                raise ValueError(f"Line {i} (old): duplicate customizable '{name}'")
                            if not default:
                                sections[name] = []

                            open_section = name
                        elif mode == EMPTY:
                            if open_section:
                                raise ValueError(f"Line {i} (old): nested customizable '{name}'")
                            if name in sections:
                                raise ValueError(f"Line {i} (old): duplicate customizable '{name}'")
                            if not default:
                                sections[name] = None
                    elif open_section and open_section in sections:
                        sections[open_section].append(line.rstrip('\r\n'))
                if open_section:
                    raise ValueError(f"Line {i} (old): unclosed customizable '{open_section}'")

        @print_to(file)
        def code():
            open_section = None
            new_sections = set()
            skip = False
            for i, line in enumerate(fn(), start=1):
                m = marker_match(line)
                if m:
                    name, mode, default = marker_info(m)
                    if mode == CLOSE:
                        if not open_section:
                            raise ValueError(f"Line {i} (new): closing unopened customizable '{name}'")
                        elif name != open_section:
                            raise ValueError(f"Line {i} (new): closing unopened customizable '{name}'"
                                             f" (open customizable is '{open_section}')")

                        if not skip:
                            yield marker_format(m, name, CLOSE, None)

                        open_section = None
                        skip = False
                    elif mode == OPEN:
                        if open_section:
                            raise ValueError(f"Line {i} (new): nested customizable '{name}'")
                        if name in new_sections:
                            raise ValueError(f"Line {i} (new): duplicate customizable '{name}'")
                        if not default:
                            raise ValueError(f"Line {i} (new): generated code must declare sections as `default`")
                        new_sections.add(name)

                        if name in sections:
                            if sections[name] is None:
                                yield marker_format(m, name, EMPTY, False)
                            else:
                                yield marker_format(m, name, OPEN, False)
                                yield from sections[name]
                                yield marker_format(m, name, CLOSE, None)
                        else:
                            yield marker_format(m, name, OPEN, True)

                        open_section = name
                        skip = name in sections
                    elif mode == EMPTY:
                        if open_section:
                            raise ValueError(f"Line {i} (new): nested customizable '{name}'")
                        if name in new_sections:
                            raise ValueError(f"Line {i} (new): duplicate customizable '{name}'")
                        if not default:
                            raise ValueError(f"Line {i} (new): generated code must declare sections as `default`")
                        new_sections.add(name)

                        if name in sections:
                            if sections[name] is None:
                                yield marker_format(m, name, EMPTY, False)
                            else:
                                yield marker_format(m, name, OPEN, False)
                                yield from sections[name]
                                yield marker_format(m, name, CLOSE, None)
                        else:
                            yield marker_format(m, name, EMPTY, True)
                elif not skip:
                    yield line
            if open_section:
                raise ValueError(f"Line {i} (new): unclosed customizable '{open_section}'")

    return decorator
