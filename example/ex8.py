from gsl import lines, generate
from gsl.antlr import Antlr

from SimpleClassLexer import SimpleClassLexer
from SimpleClassParser import SimpleClassParser
from SimpleClassVisitor import SimpleClassVisitor, Class, Field, Method

antlr = Antlr(SimpleClassLexer, SimpleClassParser)
p = antlr.parser(antlr.input_stream("""\
class HelloWorld {
    field foo;
    method bar;
}
"""))
model = p.model().accept(SimpleClassVisitor())

def class_declaration(model):
    yield from lines(f"""\
public class {model.name} {{""")
    for member in model.members:
        if isinstance(member, Field):
            yield from lines(f"""\

    private int {member.name};""")
        elif isinstance(member, Method):
            yield from lines(f"""\

    public void {member.name}() {{
        // <GSL customizable: method-{member.name}>
        // TODO
        // </GSL customizable: method-{member.name}>
    }}""")
    yield from lines(f"""\
}}""")

for class_model in model:
    @generate(f"{class_model.name}.java")
    def code():
        yield from class_declaration(class_model)
