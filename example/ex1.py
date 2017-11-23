from collections import namedtuple

Field = namedtuple('Field', ('name',))
Method = namedtuple('Method', ('name',))

def class_declaration(name, members):
    print(f"public class {name} {{")
    for member in members:
        if isinstance(member, Field):
            print(f"")
            print(f"    private int {member.name};")
        elif isinstance(member, Method):
            print(f"")
            print(f"    public void {member.name}() {{")
            print(f"        // TODO")
            print(f"    }}")
    print(f"}}")

class_declaration("HelloWorld", [Field("foo"), Method("bar")])
