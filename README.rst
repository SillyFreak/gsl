GSL - Generator Scripting Library
=================================

GSL is inspired by, but completely independent of, `iMatix' GSL`_ (Generator scripting language).
It is a Python-based tool for model-oriented programming, which you can read about `here`_,
again borrowing from iMatix.

In contrast to iMatix' GSL, this tool does not use its own scripting language but Python;
with Python 3.6's `f-strings`_, it is very appropriate for code generation tasks.
GSL's focus lies on reading the source models and making them available in a convenient form,
and providing utilities that are useful during code generation,
especially for output handling and string manipulation.

.. _iMatix' GSL: https://github.com/imatix/gsl
.. _here: https://github.com/imatix/gsl#model-oriented-programming
.. _f-strings: https://www.python.org/dev/peps/pep-0498/

Installation
------------

Installing a release
^^^^^^^^^^^^^^^^^^^^

GSL is available on pypi.
Depending on whether you want to use YAML or ANTLR models, install the extras::

    pip install gsl[antlr,yaml]

Installing for development
^^^^^^^^^^^^^^^^^^^^^^^^^^

First, clone the project and install dependencies and extras::

    pip install -e git+https://github.com/SillyFreak/gsl#egg=gsl[dev,antlr,yaml]
    # or, alternatively
    pip install invoke antlr4-python3-runtime ruamel.yaml
    git clone https://github.com/SillyFreak/gsl

We recommend using ``pip``, because that will also make the ``g4v`` shell command available.

Then, if you plan on using the ``g4v`` tool (which requires ANTLR), generate its parser and visitor::

    cd env/src/gsl/
    # or, alternatively
    cd gsl

    invoke g4v-antlr g4v-g4v

.. note::
    The ``g4v-g4v`` task overwrites the ``G4VVisitor.py`` file, which is part of the ``g4v`` tool itself.
    If you break that file, you will have to reset it from git before ``g4v-g4v`` works again.

    The same applies to incompatible changes to ``g4v``: if you extend the tool in an incompatible way,
    you will have to bootstrap ``G4VVisitor.py`` yourself.

Minimal usage example
---------------------

Model-oriented programming's benefits become most visible for complex use cases;
still, here is a small example that shows core features of GSL::

    from gsl import pseudo_tuple, lines, print_to
    from gsl.yaml import YAML

    Class = pseudo_tuple('Class', ('name', 'members',))
    Field = pseudo_tuple('Field', ('name',))
    Method = pseudo_tuple('Method', ('name',))

    def load_model():
        yaml = YAML(typ='safe')
        yaml.register_class(Class)
        yaml.register_class(Field)
        yaml.register_class(Method)
        return yaml.load("""\
        - !Class
          name: HelloWorld
          members:
          - !Field
            name: foo
          - !Method
            name: bar
        """)

    def generate_code(model):
        for class_model in model:
            generate_class_code(class_model)

    def generate_class_code(class_model):
        def field_code(field):
            yield from lines(f"""\
        private int {field.name};""")

        def method_code(method):
            yield from lines(f"""\
        public void {method.name}() {{
            // TODO
        }}""")

        @print_to(f"{class_model.name}.java")
        def code():
            yield from lines(f"""\
    public class {class_model.name} {{""")
            for member in class_model.members:
                yield from lines(f"""\

    """)
                if isinstance(member, Field):
                    yield from field_code(member)
                elif isinstance(member, Method):
                    yield from method_code(member)
            yield from lines(f"""\
    }}""")

    generate_code(load_model())

Output::

    public class HelloWorld {

        private int foo;

        public void bar() {
            // TODO
        }
    }

Some of the things seen here are:

- the use of ``pseudo_tuple`` together with YAML type tags to produce a high-level model.
  ``namedtuple`` wouldn't work here, because it is immutable
  (the YAML library separates construction and initialization of nodes to support cycles).
  Pseudo tuples are modifiable and allow auxiliary fields,
  giving you the option to augment the model with inferred information.
- ``yield`` and ``yield from`` to create the actual code piece by piece,
  without pushing side effects like ``print`` into the guts of the code generator.
  By yielding code line by line instead of writing outright to a file,
  it is easy to post-process code before writing it out.
- f-strings and a code style convention using multiline strings that aligns output code with the beginning of lines.
- separation of concerns by using different functions, and a naming convention that helps understanding these concerns:

  - ``generate_code`` generates all code for this module.
    In this case there is only one class to generate,
    but there could be multiple classes or different kinds of sources to print with no problem.
  - ``generate_..._code`` functions generate a single kind of source code.
  - ``..._code`` generator functions create the actual code by yielding it line by line.
    We use nested functions here, as fields and methods are only used for class code,
    but code reuse is of course easily possible.
  - The ``code`` generator function is a particular case.
    The ``@print_to(filename)`` decorator calls it immediately and writes all lines to the given file.
    In that sense, the whole function works like a ``with`` block, where the block body is a generator function.

If you're thinking most of this is plain Python and some coding conventions, nothing gsl specific: you're right!
Python 3.6 is already a great tool with great development environments,
and it would be a shame to take that power away from you.
GSL just provides some useful tools that, combined with Python and some conventions,
allow you to do model oriented programming at high velocity.
