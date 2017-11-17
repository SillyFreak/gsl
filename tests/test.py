import unittest

from gsl.dot_dict import DotDict


class TestDotDict(unittest.TestCase):
    def test_dot_dict(self):
        d = DotDict(a=1, b=2)

        self.assertEqual(d.a, 1)
        self.assertEqual(d['a'], 1)
        self.assertEqual(d.b, 2)
        self.assertEqual(d['b'], 2)
        with self.assertRaises(AttributeError):
            d.c
