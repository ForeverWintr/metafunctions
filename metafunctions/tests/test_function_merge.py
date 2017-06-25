import operator

from metafunctions.core import FunctionMerge
from metafunctions.core import SimpleFunction
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_str(self):
        c = FunctionMerge(operator.add, (a, b))
        self.assertEqual(str(c), '(a + b)')
        self.assertEqual(repr(c), f'FunctionMerge({operator.add}, {(a, b)})')

    def test_call(self):
        c = FunctionMerge(operator.add, (a, b))
        self.assertEqual(c('_'), '_a_b')

    def test_format(self):
        c = FunctionMerge(operator.add, (a, b), format_string='tacos')
        self.assertEqual(str(c), '(tacos)')


@SimpleFunction
def a(x):
    return x + 'a'
@SimpleFunction
def b(x):
    return x + 'b'
l = SimpleFunction(lambda x: x + 'l')
