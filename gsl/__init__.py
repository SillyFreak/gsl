from contextlib import contextmanager
import threading


__local = threading.local()


def _stack():
    try:
        return __local.stack
    except AttributeError:
        __local.stack = stack = []
        return stack


@contextmanager
def file(name):
    stack = _stack()
    with open(name, "w") as f:
        stack.append(f)
        try:
            yield
        finally:
            stack.pop()


def output(string):
    stack = _stack()
    file = stack[-1] if len(stack) > 0 else None
    print(string, file=file)
