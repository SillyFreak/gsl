import unittest
import os

from gsl import lines, generate, print_to
from gsl.dot_dict import DotDict
from gsl.antlr import Antlr
from gsl.yaml import YAML


class TestDotDict(unittest.TestCase):
    def test_dot_dict(self):
        d = DotDict(a=1, b=2)

        self.assertEqual(d.a, 1)
        self.assertEqual(d['a'], 1)
        self.assertEqual(d.b, 2)
        self.assertEqual(d['b'], 2)
        with self.assertRaises(AttributeError):
            d.c


class TestYaml(unittest.TestCase):
    def test_yaml(self):
        yaml = YAML(typ='safe')
        model = yaml.load("""\
world: df
hello:
- a
- b: 1
""")

        self.assertEqual(model.world, "df")
        self.assertEqual(model['world'], "df")
        self.assertEqual(model.hello[0], "a")
        self.assertEqual(model['hello'][0], "a")
        self.assertEqual(model.hello[1].b, 1)
        self.assertEqual(model['hello'][1].b, 1)


class TestAntlr(unittest.TestCase):
    def test_antlr_set(self):
        from tests.grammar.SetTestLexer import SetTestLexer
        from tests.grammar.SetTestParser import SetTestParser
        from tests.grammar.SetTestVisitor import SetTestVisitor as _SetTestVisitor

        class SetTestVisitor(_SetTestVisitor):
            def visitIntElement(self, ctx: SetTestParser.IntElementContext):
                return int(super(SetTestVisitor, self).visitIntElement(ctx))

        antlr = Antlr(SetTestLexer, SetTestParser)

        p = antlr.parser(antlr.input_stream("{1, 2, {}, {3}}"))
        expr = antlr.parse_safe(p.expr)
        model = expr.accept(SetTestVisitor())

        self.assertEqual(model, [1, 2, [], [3]])

    def test_antlr_expr(self):
        from tests.grammar.ExprTestLexer import ExprTestLexer
        from tests.grammar.ExprTestParser import ExprTestParser
        from tests.grammar.ExprTestVisitor import ExprTestVisitor as _ExprTestVisitor

        class ExprTestVisitor(_ExprTestVisitor):
            def visitNumber(self, ctx: ExprTestParser.NumberContext):
                return int(super(ExprTestVisitor, self).visitNumber(ctx))

        antlr = Antlr(ExprTestLexer, ExprTestParser)

        p = antlr.parser(antlr.input_stream("1 + 2 * 3 + (4 + 5)"))
        expr = antlr.parse_safe(p.expr)
        model = expr.accept(ExprTestVisitor())

        self.assertEqual(model, [[1], '+', [2, '*', 3], '+', [[[4], '+', [5]]]])

    def test_antlr_hedgehog(self):
        file = '''\
io.AnalogMessage analog_message = 3 {
  """Request or reply for one analog sensor's value"""

  uint32 port = 1 {
    Python: "int";
    TypeScript: "number";
  }
  uint32 value = 2 {
    Python: "int";
    TypeScript: "number";
  }
  Subscription subscription = 3 {
    Python: "Subscription";
    TypeScript: "Subscription";
  }

  => analog.Request(port)
    """analog request => analog reply""";
  <= analog.Reply(port, value)
    """analog reply""";
  => analog.Subscribe(port, subscription)
    """analog subscribe => ack""";
  <- analog.Update(port, value, subscription)
    """analog update""";
}

motor.MotorAction motor_action = 5 {
  """Command for one motor. By setting a relative or absolute goal position,
the motor will go into `reached_state` upon reaching the position."""

  uint32 port = 1 {
    Python: "int";
    TypeScript: "number";
  }
  MotorState state = 2 {
    Python: "int";
    TypeScript: "number";
  }
  sint32 amount = 3 {
    Python: "int", "0";
    TypeScript: "number", "0";
  }
  MotorState reached_state = 4 {
    Python: "int", "POWER";
    TypeScript: "number", "MotorState.POWER";
  }
  oneof position {
    sint32 relative = 5 {
      Python: "int";
      TypeScript: "number";
    }
    sint32 absolute = 6 {
      Python: "int";
      TypeScript: "number";
    }
  }

  => motor.Action(port, state, amount, [reached_state, relative/absolute])
    """motor action => ack""";
}

process.ProcessExecuteAction process_execute_action = 20 {
  """Invoke a process on the controller"""

  repeated string args = 2 {
    Python: "str";
    TypeScript: "string[]";
  }
  string working_dir = 1 {
    Python: "str", "None";
    TypeScript: "string", "undefined";
  }

  => process.ExecuteAction(*args, [working_dir])
    """process execute action => process execute reply""";
}
'''

        from tests.grammar.HedgehogTestLexer import HedgehogTestLexer
        from tests.grammar.HedgehogTestParser import HedgehogTestParser
        from tests.grammar.HedgehogTestVisitor import HedgehogTestVisitor as _HedgehogTestVisitor

        class HedgehogTestVisitor(_HedgehogTestVisitor):
            def visitNumber(self, ctx: HedgehogTestParser.NumberContext):
                return int(super(HedgehogTestVisitor, self).visitNumber(ctx))

        antlr = Antlr(HedgehogTestLexer, HedgehogTestParser)

        p = antlr.parser(antlr.input_stream(file))
        expr = p.expr()
        model = expr.accept(HedgehogTestVisitor())

        for message in model:
            print("{m.messageType} {m.discriminator} = {m.label}".format(m=message))
            print("    {m.docstring}".format(m=message))
            for field in message.fields:
                print("    {}".format(field))


class TestGenerate(unittest.TestCase):
    def assertFileEqual(self, file, content):
        with open(file) as f:
            self.assertEqual(f.read(), content)


    def test_generate(self):
        try:
            os.remove('tests/test_output')
        except FileNotFoundError:
            pass

        @generate('tests/test_output')
        def code():
            yield from lines("""\
generated header
# <default GSL customizable: body>
generated body
# </GSL customizable: body>
generated footer
""")

        self.assertFileEqual('tests/test_output', """\
generated header
# <default GSL customizable: body>
generated body
# </GSL customizable: body>
generated footer
""")

        @print_to('tests/test_output')
        def code():
            yield from lines("""\
generated header
# <default GSL customizable: body>
CUSTOMIZED body
# </GSL customizable: body>
generated footer
""")

        @generate('tests/test_output')
        def code():
            yield from lines("""\
new generated header
# <default GSL customizable: body>
new generated body
# </GSL customizable: body>
new generated footer
""")

        self.assertFileEqual('tests/test_output', """\
new generated header
# <default GSL customizable: body>
new generated body
# </GSL customizable: body>
new generated footer
""")

        @print_to('tests/test_output')
        def code():
            yield from lines("""\
generated header
# <GSL customizable: body>
CUSTOMIZED body
# </GSL customizable: body>
generated footer
""")

        @generate('tests/test_output')
        def code():
            yield from lines("""\
newest generated header
# <default GSL customizable: body>
newest generated body
# </GSL customizable: body>
newest generated footer
""")

        self.assertFileEqual('tests/test_output', """\
newest generated header
# <GSL customizable: body>
CUSTOMIZED body
# </GSL customizable: body>
newest generated footer
""")

        os.remove('tests/test_output')
