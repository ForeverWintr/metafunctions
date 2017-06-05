import operator

from function_pipe.meta_function import FunctionMerge
from function_pipe.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_str(self):
        c = FunctionMerge(operator.add, (a, b))
        self.assertEqual(str(c), '(a + b)')
        self.assertEqual(repr(c), f'FunctionMerge({operator.add}, {(a, b)})')

    def test_call(self):
        c = FunctionMerge((a, b, l))
        self.assertEqual(c('_'), '_abl')



def a(x):
    return x + 'a'
def b(x):
    return x + 'b'
l = lambda x: x + 'l'
