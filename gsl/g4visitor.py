import os.path
from antlr4 import FileStream
from . import file, output
from .antlr import Antlr, ParseTreeVisitor

from .grammar.G4VisitorLexer import G4VisitorLexer
from .grammar.G4VisitorParser import G4VisitorParser
from .grammar.G4VisitorVisitor import *
from .grammar.G4VisitorVisitor import G4VisitorVisitor as _G4VisitorVisitor


class G4VisitorVisitor(_G4VisitorVisitor):
    def visitAttributeRef(self, ctx:G4VisitorParser.AttributeRefContext):
        return super(G4VisitorVisitor, self).visitAttributeRef(ctx)[1:-1]


def process(in_file, out_file=None):
    antlr = Antlr(G4VisitorLexer, G4VisitorParser)
    p = antlr.parser(FileStream(in_file))
    model = p.visitor().accept(G4VisitorVisitor())

    dirname = os.path.dirname(in_file)
    basename, ext = os.path.splitext(os.path.basename(in_file))
    if basename != model.name or ext != '.g4v':
        raise ValueError(f"Expected visitor in file '{model.name}.g4v', not in'{basename}{ext}'.")

    if out_file is None:
        out_file = os.path.join(dirname, basename + '.py')

    def cap(str):
        return str[0:1].upper() + str[1:]

    def processVisitor(visitor):
        visitorName, grammarName, rules = visitor

        output(f"""\
from collections import namedtuple

from gsl.antlr import ParseTreeVisitor
from .{grammarName}Parser import {grammarName}Parser

""")
        for ruleName, body in rules:
            if isinstance(body, ObjectBody):
                objectName, params = body
                paramsStr = ' '.join(f"{param.name!r}," for param in params)
                output(f"""\
{objectName} = namedtuple({objectName!r}, ({paramsStr}))""")

        output(f"""\


class {visitorName}(ParseTreeVisitor):""")
        for ruleName, body in rules:
            output(f"""\
    def visit{cap(ruleName)}(self, ctx: {grammarName}Parser.{cap(ruleName)}Context):""")
            processBody(body)
            output(f"""\
""")

    def processBody(body):
        if isinstance(body, ObjectBody):
            processObjectBody(body)
        else:
            processExprBody(body)

    def processObjectBody(objectBody):
        output(f"""\
        return {objectBody.name}(""")
        for paramName, expr, optional in objectBody.params:
            opt = f" if {processExprCore(expr, True)} else None" if optional else ""
            output(f"""\
            {processExpr(expr)}{opt},""")
        output(f"""\
        )""")

    def processExprBody(exprBody):
        output(f"""\
        return {processExpr(exprBody)}""")

    def processExprCore(expr, check=False):
        if isinstance(expr, RuleExpr):
            args = "ctx" + ''.join(f", {model.grammar}Parser.{cap(t)}Context" for t in expr.rules)
            operation = "self.get_children" if check or expr.multi else "self.get_child"
            return f"{operation}({args})"
        elif isinstance(expr, TokenExpr):
            return f"ctx.{expr.token}()"
        elif isinstance(expr, RefExpr):
            return f"ctx.{expr.ref}"

    def processExpr(expr):
        core = processExprCore(expr)
        operation = "bool" if expr.presence else "self.visitNode" if isinstance(expr, RefExpr) or not expr.multi else "self.visitNodes"
        return f"{operation}({core})"

    with file(out_file):
        processVisitor(model)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('in_files', metavar='in_file', nargs='+')
    parser.add_argument('-o', '--out_file', default=None,
                        help="if there is only one input file, use this as the output file")

    args = parser.parse_args()

    if args.out_file is not None and len(args.in_files) > 1:
        print("explicit out_file only allowed for a single in_file")

    for in_file in args.in_files:
        process(in_file, args.out_file)


if __name__ == '__main__':
    main()
