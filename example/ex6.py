from gsl import pseudo_tuple, file, output
from gsl.antlr import Antlr, ParseTreeVisitor

from SimpleClassLexer import SimpleClassLexer
from SimpleClassParser import SimpleClassParser

antlr = Antlr(SimpleClassLexer, SimpleClassParser)
p = antlr.parser(antlr.input_stream("""\
class HelloWorld {
    field foo;
    method bar;
}
"""))

Class = pseudo_tuple('Class', ('name', 'members',))
Field = pseudo_tuple('Field', ('name',))
Method = pseudo_tuple('Method', ('name',))

class SimpleClassVisitor(ParseTreeVisitor):
    def visitModel(self, ctx):
        return self.visitNodes(self.get_children(ctx, SimpleClassParser.ClassDefContext))

    def visitClassDef(self, ctx):
        return Class(
            self.visitNode(ctx.IDENTIFIER()),
            self.visitNodes(self.get_children(ctx, SimpleClassParser.FieldDefContext, SimpleClassParser.MethodDefContext)),
        )

    def visitFieldDef(self, ctx):
        return Field(self.visitNode(ctx.IDENTIFIER()))

    def visitMethodDef(self, ctx):
        return Method(self.visitNode(ctx.IDENTIFIER()))

model = p.model().accept(SimpleClassVisitor())

print(model)
