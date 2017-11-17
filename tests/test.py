import unittest

from gsl.dot_dict import DotDict
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
