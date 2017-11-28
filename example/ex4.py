from gsl import pseudo_tuple, lines, printlines
from gsl.yaml import YAML

Class = pseudo_tuple('Class', ('name', 'members',))
Field = pseudo_tuple('Field', ('name',))
Method = pseudo_tuple('Method', ('name',))

yaml = YAML(typ='safe')
yaml.register_class(Class)
yaml.register_class(Field)
yaml.register_class(Method)
model = yaml.load("""\
- !Class
  name: HelloWorld
  members:
  - !Field
    name: foo
  - !Method
    name: bar
""")

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

for class_model in model:
    with open(f"{class_model.name}.java", "w") as f:
        printlines(class_declaration(class_model), file=f)
