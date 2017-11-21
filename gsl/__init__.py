from contextlib import contextmanager
import re
import threading

from antlr4 import FileStream, CommonTokenStream, BailErrorStrategy

from .grammar.GSLLexer import GSLLexer
from .grammar.GSLParser import GSLParser
from .grammar.GSLVisitor import GSLVisitor as _GSLVisitor


class GSLVisitor(_GSLVisitor):
    def visitGsl(self, ctx):
        def lines():
            n = ctx.getChildCount() - 1

            if n % 2 == 1:
                # first line does not have a NEWLINE
                t, content = ctx.getChild(0).accept(self)
                yield "", "", t, content

            for i in range(n % 2, n, 2):
                newline = ctx.getChild(i).accept(self)
                eol = re.sub(r'[^\r\n\f]', '', newline)
                indent = re.sub(r'[\r\n\f]', '', newline)
                t, content = ctx.getChild(i + 1).accept(self)
                yield eol, indent, t, content

        def processed():
            def process(eol, indent, t, content):
                if t is None:
                    return '{}{}{}'.format(eol, indent, content)
                elif t in {'>', '>"""'}:
                    return '{}{}output("""\\\n{}\\\n""")'.format(eol, indent, content)
                elif t in {'`', '`"""'}:
                    return '{}{}output(f"""\\\n{}\\\n""")'.format(eol, indent, content)

            backlog = []
            for eol, indent, t, content in lines():
                if t is not None and indent == "":
                    backlog.append((eol, t, content))
                else:
                    for _eol, _t, _content in backlog:
                        yield process(_eol, indent, _t, _content)
                    backlog.clear()
                    yield process(eol, indent, t, content)
            for _eol, _t, _content in backlog:
                yield process(_eol, "", _t, _content)
            backlog.clear()

        return ''.join(processed())

    def visitCode(self, ctx):
        return None, ctx.CODE().accept(self)

    def visitTemplate(self, ctx):
        return '>', ctx.TEMPLATE().accept(self)[1:]

    def visitFTemplate(self, ctx):
        return '`', ctx.FTEMPLATE().accept(self)[1:]

    def visitString(self, ctx):
        pattern = re.compile(r'^>"""(?:\r?\n|\r|\f)(.*)(?:\r?\n|\r|\f)[ \t]*>"""$', flags=re.DOTALL)
        string = ctx.STRING().accept(self)
        payload = pattern.match(string).group(1)
        return '>"""', payload

    def visitFString(self, ctx):
        pattern = re.compile(r'^`"""(?:\r?\n|\r|\f)(.*)(?:\r?\n|\r|\f)[ \t]*`"""$', flags=re.DOTALL)
        string = ctx.FSTRING().accept(self)
        payload = pattern.match(string).group(1)
        return '`"""', payload

    def visitEmptyLine(self, ctx):
        return None, ""

    def visitTerminal(self, node):
        return node.symbol.text


def process_file(file):
    input = FileStream(file)

    lexer = GSLLexer(input)
    lexer.removeErrorListeners()

    tokens = CommonTokenStream(lexer)

    parser = GSLParser(tokens)
    parser.removeErrorListeners()
    parser._errHandler = BailErrorStrategy()

    return parser.gsl().accept(GSLVisitor())


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


# def load(name):
#     class DotDoc(object):
#         def __init__(self, wrapped):
#             self.wrapped = wrapped
#
#     loaded = yaml.safe_load(open('hedgehog_protocol.yml'))
