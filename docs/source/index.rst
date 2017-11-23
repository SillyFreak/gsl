.. _home:

GSL - Generator Scripting Library
=================================

GSL is inspired by, but completely independent of, `iMatix' GSL`_ (Generator scripting language).
It is a Python-based tool for model-oriented programming, which you can read about `here`_,
again borrowing from iMatix.

In contrast to iMatix' GSL, this tool does not use its own scripting language but Python;
with Python 3.6's `f-strings`_, it is very appropriate for code generation tasks.
GSL's focus lies on reading the source models and making them available in a convenient form,
and providing utilities that are useful during code generation, especially for string manipulation.

.. _iMatix' GSL: https://github.com/imatix/gsl
.. _here: https://github.com/imatix/gsl#model-oriented-programming
.. _f-strings: https://www.python.org/dev/peps/pep-0498/

Python code generation examples
-------------------------------

Actual code generation in Python is pretty straightforward and can be done with or without GSL.
We will describe here some guidelines that can help keep code generation code more readable.

Generally speaking, a code generator will contain code in two languages:
the generator language (here, Python 3.6+), and the target language (in our examples Java).
This makes the code inherently more difficult to read, calling for good tools and conventions.
In Python, target language code will appear in string literals.
Consider this simple code generator::

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

Which outputs::

    public class HelloWorld {

        public void foo() {
            // TODO
        }

        public void bar() {
            // TODO
        }
    }

The generator code is nicely readable, but target code readability suffers from the different indentation levels.
Separate ``print`` statements don't hurt, but depend on one's taste.
We advocate for the following style::

    from collections import namedtuple

    Field = namedtuple('Field', ('name',))
    Method = namedtuple('Method', ('name',))

    def class_declaration(name, members):
        print(f"""\
    public class {name} {{""")
        for member in members:
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

    class_declaration("HelloWorld", [Field("foo"), Method("bar")])

This code has a different readability tradeoff.
Generator code indentation is interrupted by target code,
but in return each target code line's indentation is directly apparent.
The ``\`` at the start of each literal ignores the following line break,
allowing the first line of the literal to start at the same level as the rest.

Adding GSL
^^^^^^^^^^

At this level of abstraction, GSL's main use comes from output handling.
Right now, generated code goes to standard output.
GSL allows to easily specify the target file for any output::

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

(without any ``file`` open, output still goes to stdout,
so ``output`` can be used even before specifying the destination.

YAML
----

GSL provides a thin wrapper around the `ruamel.yaml`_ YAML library::

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

The model is a little different; instead of ``Field('foo')``, ``{'field': 'foo'}`` is used here.
That helps us keep the YAML readable.

The one difference from normal YAML usage is in the accesses like ``model.name``.
Regularly, the YAML parser uses plain ``dict`` s here, requiring ``model['name']`` etc.
That (and all other ``dict`` functionality) is still there,
but dot-access is added as it is often more readable and makes sense for many models.

.. _ruamel.yaml: http://yaml.readthedocs.io/en/latest/overview.html

ANTLR
-----

Often, a model based on YAML (or any other markup language) is enough to describe a model concisely,
but there are cases where a DSL (domain specific language) boosts expresiveness immensely.
In these cases, `ANTLR`_ can be used to parse the DSL, and GSL to process the parse tree.

Let's first write a grammar that lets us express this simple model::

    class HelloWorld {
        field foo;
        method bar;
    }

We will not go into detail about writing grammars here and simply give it::

    grammar SimpleClass;

    model: classDef* EOF;

    classDef: 'class' name=IDENTIFIER '{' (fieldDef | methodDef)* '}';
    fieldDef: 'field' name=IDENTIFIER ';';
    methodDef: 'method' name=IDENTIFIER ';';

    IDENTIFIER: [_a-zA-Z][a-zA-Z0-9]*;

    WS: [ \t]+ -> channel(HIDDEN);

Then, generate lexer and parser from this grammar::

    antlr4 -Dlanguage=Python3 -visitor -no-listener SimpleClass.g4

And finally, write a simple program that parses our model::

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

    print(antlr.to_string(model))

The ``Antlr`` class provides us with convenience methods for using our grammar.
As a first step, we simply print the parse tree to better understand what's happening here::

    (model (classDef class HelloWorld { (fieldDef field foo ;) (methodDef method bar ;) }) <EOF>)

The parse tree contains all tokens consumed, including ``class``, ``method``, ``<EOF>`` etc.,
that were important for parsing but don't add anything to the model.
We can already generate code from this model::

    from gsl import file, output

    # ...

    def class_declaration(model):
        output(f"""\
    public class {model.IDENTIFIER()} {{""")
        for member in model.getChildren():
            if isinstance(member, SimpleClassParser.FieldDefContext):
                output(f"""\

        private int {member.IDENTIFIER()};""")
            elif isinstance(member, SimpleClassParser.MethodDefContext):
                output(f"""\

        public void {member.IDENTIFIER()}() {{
            // TODO
        }}""")
        output(f"""\
    }}""")

    for class_model in model.classDef():
        with file(f"{class_model.IDENTIFIER()}.java"):
            class_declaration(class_model)

This code has a slight downside: ``getChildren()`` returns all children,
not only the fields and methods we're interested in.
We filter out the other children inside the loop, yes,
but being able to get specific kinds of children would be good in its own right.

.. _ANTLR: http://www.antlr.org/

Parse tree transformation with visitors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We could use ``fieldDef()`` and ``methodDef()`` to get fields and methods separately,
but then we lose their relative order.
Also, ``IDENTIFIER()`` is not really expressive.
What we really want is a model that reflects our needs:
ignore semicolons and list fields and methods together.
ANTLR provides visitors for doing parse tree transformations,
and GSL adds its own APIs and DSL (g4v) for making it as seamless as possible.

Let's create a visitor to process our parse tree.. ::

    from collections import namedtuple
    from gsl.antlr import ParseTreeVisitor

    # ...

    Class = namedtuple('Class', ('name', 'members',))
    Field = namedtuple('Field', ('name',))
    Method = namedtuple('Method', ('name',))

    class SimpleClassVisitor(ParseTreeVisitor):
        def visitModel(self, ctx):
            return self.visitNodes(self.get_children(ctx, SimpleClassParser.ClassDefContext))

        def visitClassDef(self, ctx):
            return Class(
                self.visitNode(ctx.IDENTIFIER()),
                self.visitNodes(self.get_children(ctx, SimpleClassParser.FieldDefContext, SimpleClassParser.MethodDefContext)),
            )

        def visitFieldDef(self, ctx):
            return Field(self.visitNode(ctx.IDENTIFIER()))

        def visitMethodDef(self, ctx):
            return Method(self.visitNode(ctx.IDENTIFIER()))

    print(model.accept(SimpleClassVisitor()))

... and take a look at the result::

    [Class(name='HelloWorld', members=[Field(name='foo'), Method(name='bar')])]

Very readable!
Before we integrate this into the rest of our code, let's automate the creation of this visitor:

ANTLR 4 Visitors DSL (g4v)
^^^^^^^^^^^^^^^^^^^^^^^^^^

A visitor for creating a concise data structure like above is fairly straight-forward,
and in many cases can be created automatically.
Even if some parts do not follow strict patterns,
subclassing allows one to use a generated visitor as the baseline.

Using g4v, the visitor from the previous section can be defined as follows::

    visitor SimpleClassVisitor for grammar SimpleClass;

    model = classDef*;
    classDef = Class(name=IDENTIFIER, members=(fieldDef | methodDef)*);
    fieldDef = Field(name=IDENTIFIER);
    methodDef = Method(name=IDENTIFIER);

Then, create the visitor from this (overwriting the file created by ANTLR::

    g4v SimpleClassVisitor.g4v

And finally, the full code generator::

    from gsl import file, output
    from gsl.antlr import Antlr

    from SimpleClassLexer import SimpleClassLexer
    from SimpleClassParser import SimpleClassParser
    from SimpleClassVisitor import SimpleClassVisitor, Class, Field, Method

    antlr = Antlr(SimpleClassLexer, SimpleClassParser)
    p = antlr.parser(antlr.input_stream("""\
    class HelloWorld {
        field foo;
        method bar;
    }
    """))
    model = p.model().accept(SimpleClassVisitor())

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

Learn More
----------

.. toctree::
    :maxdepth: 2

TODOs
-----

.. todolist::
