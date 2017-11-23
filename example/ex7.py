from gsl import file, output
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
    output(f"""\
public class {model.name} {{""")
    for member in model.members:
        if isinstance(member, Field):
            output(f"""\

    private int {member.name};""")
        elif isinstance(member, Method):
            output(f"""\

    public void {member.name}() {{
        // TODO
    }}""")
    output(f"""\
}}""")

for class_model in model:
    with file(f"{class_model.name}.java"):
        class_declaration(class_model)
