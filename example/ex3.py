from collections import namedtuple
from gsl import file, output

Field = namedtuple('Field', ('name',))
Method = namedtuple('Method', ('name',))

def class_declaration(name, members):
    output(f"""\
public class {name} {{""")
    for member in members:
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
    class_declaration("HelloWorld", [Field("foo"), Method("bar")])
