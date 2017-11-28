from gsl import lines, printlines
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
    yield from lines(f"""\
public class {model.IDENTIFIER()} {{""")
    for member in model.getChildren():
        if isinstance(member, SimpleClassParser.FieldDefContext):
            yield from lines(f"""\

    private int {member.IDENTIFIER()};""")
        elif isinstance(member, SimpleClassParser.MethodDefContext):
            yield from lines(f"""\

    public void {member.IDENTIFIER()}() {{
        // TODO
    }}""")
    yield from lines(f"""\
}}""")

for class_model in model.classDef():
    with open(f"{class_model.IDENTIFIER()}.java", "w") as f:
        printlines(class_declaration(class_model), file=f)
