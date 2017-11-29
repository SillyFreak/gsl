import os.path
from antlr4 import FileStream
from . import lines, print_to
from .antlr import Antlr

from .grammar.G4VisitorLexer import G4VisitorLexer
from .grammar.G4VisitorParser import G4VisitorParser
from .grammar.G4VVisitor import *


class G4VisitorVisitor(G4VVisitor):
    def visitAttributeRef(self, ctx:G4VisitorParser.AttributeRefContext):
        return super(G4VisitorVisitor, self).visitAttributeRef(ctx)[1:-1]


def generate_code(in_file, out_file=None):
    antlr = Antlr(G4VisitorLexer, G4VisitorParser)
    p = antlr.parser(FileStream(in_file))
    model = p.visitor().accept(G4VisitorVisitor())

    dirname = os.path.dirname(in_file)
    basename, ext = os.path.splitext(os.path.basename(in_file))
    if basename != model.name or ext != '.g4v':
        raise ValueError(f"Expected visitor in file '{model.name}.g4v', not in'{basename}{ext}'.")

    if out_file is None:
        out_file = os.path.join(dirname, basename + '.py')

    @print_to(out_file)
    def code():
        def cap(str):
            return str[0:1].upper() + str[1:]

        def visitor_code(visitor):
            visitorName, grammarName, rules = visitor

            yield from lines(f"""\
from gsl import pseudo_tuple

from gsl.antlr import ParseTreeVisitor
if __name__ is not None and "." in __name__:
    from .{grammarName}Parser import {grammarName}Parser
else:
    from {grammarName}Parser import {grammarName}Parser


""")
            for ruleName, body in rules:
                if isinstance(body, ObjectBody):
                    objectName, params = body
                    paramsStr = ' '.join(f"{param.name!r}," for param in params)
                    yield from lines(f"""\
{objectName} = pseudo_tuple({objectName!r}, ({paramsStr}))""")

            yield from lines(f"""\


class {visitorName}(ParseTreeVisitor):""")
            for ruleName, body in rules:
                yield from lines(f"""\
    def visit{cap(ruleName)}(self, ctx: {grammarName}Parser.{cap(ruleName)}Context):""")
                yield from body_code(body)
                yield from lines(f"""\

""")

        def body_code(body):
            if isinstance(body, ObjectBody):
                yield from object_body_code(body)
            else:
                yield from expr_body_code(body)

        def object_body_code(objectBody):
            yield from lines(f"""\
        return {objectBody.name}(""")
            for paramName, expr, optional in objectBody.params:
                opt = f" if {expr_core_str(expr, True)} else None" if optional else ""
                yield from lines(f"""\
            {expr_str(expr)}{opt},""")
            yield from lines(f"""\
        )""")

        def expr_body_code(exprBody):
            yield from lines(f"""\
        return {expr_str(exprBody)}""")

        def expr_core_str(expr, check=False):
            if isinstance(expr, RuleExpr):
                args = "ctx" + ''.join(f", {model.grammar}Parser.{cap(t)}Context" for t in expr.rules)
                operation = "self.has_children" if check else "self.get_children" if expr.multi else "self.get_child"
                return f"{operation}({args})"
            elif isinstance(expr, TokenExpr):
                return f"ctx.{expr.token}()"
            elif isinstance(expr, RefExpr):
                return f"ctx.{expr.ref}"

        def expr_str(expr):
            core = expr_core_str(expr)
            operation = "bool" if expr.presence else "self.visitNode" if isinstance(expr, RefExpr) or not expr.multi else "self.visitNodes"
            return f"{operation}({core})"

        yield from visitor_code(model)


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
        generate_code(in_file, args.out_file)


if __name__ == '__main__':
    main()
