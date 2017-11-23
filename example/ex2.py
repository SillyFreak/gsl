from collections import namedtuple

Class = namedtuple('Class', ('name', 'members',))
Field = namedtuple('Field', ('name',))
Method = namedtuple('Method', ('name',))

model = Class("HelloWorld", [Field("foo"), Method("bar")])

def class_declaration(model):
    print(f"""\
public class {model.name} {{""")
    for member in model.members:
        if isinstance(member, Field):
            print(f"""\

    private int {member.name};""")
        elif isinstance(member, Method):
            print(f"""\

    public void {member.name}() {{
        // TODO
    }}""")
    print(f"""\
}}""")

class_declaration(model)
