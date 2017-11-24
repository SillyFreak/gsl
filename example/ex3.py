from gsl import pseudo_tuple, file, output

Class = pseudo_tuple('Class', ('name', 'members',))
Field = pseudo_tuple('Field', ('name',))
Method = pseudo_tuple('Method', ('name',))

model = Class("HelloWorld", [Field("foo"), Method("bar")])

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

with file("HelloWorld.java"):
    class_declaration(model)
