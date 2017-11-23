from gsl import file, output
from gsl.antlr import Antlr

from SimpleClassLexer import SimpleClassLexer
from SimpleClassParser import SimpleClassParser

antlr = Antlr(SimpleClassLexer, SimpleClassParser)
p = antlr.parser(antlr.input_stream("""\
class HelloWorld {
    field foo;
    method bar;
}
"""))
model = p.model()

def class_declaration(model):
    output(f"""\
public class {model.IDENTIFIER()} {{""")
    for member in model.getChildren():
        if isinstance(member, SimpleClassParser.FieldDefContext):
            output(f"""\

    private int {member.IDENTIFIER()};""")
        elif isinstance(member, SimpleClassParser.MethodDefContext):
            output(f"""\

    public void {member.IDENTIFIER()}() {{
        // TODO
    }}""")
    output(f"""\
}}""")

for class_model in model.classDef():
    with file(f"{class_model.IDENTIFIER()}.java"):
        class_declaration(class_model)
