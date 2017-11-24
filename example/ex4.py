from gsl import pseudo_tuple, file, output
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

print(model)

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
