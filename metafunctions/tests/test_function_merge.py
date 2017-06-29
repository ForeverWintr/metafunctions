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
        c = FunctionMerge(operator.add, (a, b), join_str='tacos')
        self.assertEqual(str(c), '(a tacos b)')

    def test_non_binary(self):
        # I don't currently have any non binary functionMerges, but they're designed to be possible
        def concat(*args):
            return ''.join(args)

        c = FunctionMerge(concat, (a, a, a, a))
        self.assertEqual(c('_'), '_a_a_a_a')

        self.assertEqual(str(c), f'(a {concat} a {concat} a {concat} a)')

        d = FunctionMerge(concat, (b, b), join_str='q')
        self.assertEqual(str(d), '(b q b)')



@SimpleFunction
def a(x):
    return x + 'a'
@SimpleFunction
def b(x):
    return x + 'b'
l = SimpleFunction(lambda x: x + 'l')
