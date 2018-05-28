from antlr4 import InputStream, FileStream, CommonTokenStream
from antlr4.error.Errors import ParseCancellationException
from antlr4.error.ErrorListener import ErrorListener
from .dot_dict import DotDict


class ParseTreeVisitor(object):
    # mandatory visitor methods

    def visitChildren(self, node, *types):
        return self.visitNodes(self.get_children(node, *types))

    def visitTerminal(self, node):
        return node.symbol.text

    def visitErrorNode(self, node):
        return None

    # convenience visitor methods

    def visitChild(self, node, *types):
        return self.visitNode(self.get_child(node, *types))

    def visitNodes(self, nodes):
        return [node.accept(self) for node in nodes]

    def visitNode(self, node):
        return node.accept(self)

    # auxillary methods

    def get_children(self, node, *types):
        return (child for child in node.getChildren() if len(types) == 0 or isinstance(child, types))

    def has_children(self, node, *types):
        it = self.get_children(node, *types)
        try:
            next(it)
        except StopIteration:
            return False
        else:
            return True

    def get_child(self, node, *types):
        child, = self.get_children(node, *types)
        return child

    def collapse(self, nodes, *, constructor=None, name=None):
        if constructor is not None and name is not None:
            raise ValueError("constructor and name are mutually exclusive")
        try:
            node, = nodes
        except ValueError:
            if constructor is not None:
                return constructor(nodes)
            elif name is not None:
                return {name: nodes}
            else:
                return nodes
        else:
            return node

    def get_text(self, node):
        return node.getText()

    def get_full_text(self, node):
        return node.parser.getTokenStream().getText(node.getSourceInterval())


class DotDictVisitorMixin(object):
    def visitChildren(self, node):
        result = DotDict()
        result[self.rule_name(node)] = [child.accept(self) for child in node.getChildren()]
        return result

    def aggregateResult(self, aggregate, nextResult):
        aggregate[nextResult] = None
        return aggregate

    def visitTerminal(self, node):
        return self.token_name(node.symbol)

    def rule_name(self, node):
        return self.Parser.ruleNames[node.getRuleIndex()]

    def token_name(self, token):
        return token.text

    # convenience methods

    def visitSingleChild(self, node):
        assert node.getChildCount() == 1, "visitSingleChild() requires there to be only one child"
        return node.getChild(0).accept(self)


def dot_dict_visitor(_Parser, _Visitor):
    class Visitor(DotDictVisitorMixin, _Visitor):
        Parser = _Parser

    return Visitor


class BailErrorListener(ErrorListener):
    INSTANCE = None

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ParseCancellationException(f"line {line}:{column} {msg}")


BailErrorListener.INSTANCE = BailErrorListener()


class Antlr(object):
    def __init__(self, Lexer=None, Parser=None):
        self.Lexer = Lexer
        self.Parser = Parser

    def input_stream(self, text):
        return InputStream(text)

    def file_stream(self, file, encoding='ascii', errors='strict'):
        return FileStream(file, encoding, errors)

    def lexer(self, input):
        lexer = self.Lexer(input)
        lexer.removeErrorListeners()
        return lexer

    def token_stream(self, input):
        return CommonTokenStream(self.lexer(input))

    def parser(self, input):
        parser = self.Parser(self.token_stream(input))
        parser.removeErrorListeners()
        parser.addErrorListener(BailErrorListener.INSTANCE)
        return parser

    def visitor(self, Visitor):
        return dot_dict_visitor(self.Parser, Visitor)

    def to_string(self, ctx):
        return ctx.toStringTree(self.Parser.ruleNames, self.Parser)

    def parse_safe(self, parse):
        try:
            return parse()
        except ParseCancellationException:
            return None
