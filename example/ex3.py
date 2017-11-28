from gsl import pseudo_tuple, lines, printlines

Class = pseudo_tuple('Class', ('name', 'members',))
Field = pseudo_tuple('Field', ('name',))
Method = pseudo_tuple('Method', ('name',))

model = Class("HelloWorld", [Field("foo"), Method("bar")])

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
        // TODO
    }}""")
    yield from lines(f"""\
}}""")

def commented(code, block=False):
    if block:
        yield "/*"
    for line in code:
        yield (" * " if block else "// ") + line
    if block:
        yield " */"

with open("HelloWorld.java", "w") as f:
    printlines(class_declaration(model), file=f)
