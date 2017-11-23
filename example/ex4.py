from collections import namedtuple
from gsl import file, output
from gsl.yaml import YAML

def class_declaration(model):
    output(f"""\
public class {model.name} {{""")
    for member in model.members:
        if 'field' in member:
            output(f"""\

    private int {member.field};""")
        elif 'method' in member:
            output(f"""\

    public void {member.method}() {{
        // TODO
    }}""")
    output(f"""\
}}""")

yaml = YAML(typ='safe')
model = yaml.load("""\
- name: HelloWorld
  members:
  - field: foo
  - method: bar
""")

for class_model in model:
    with file(f"{class_model.name}.java"):
        class_declaration(class_model)
