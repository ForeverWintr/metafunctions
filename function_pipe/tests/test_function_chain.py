
from function_pipe.meta_function import FunctionChain
from function_pipe.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_str(self):
        c = FunctionChain((a, b, l))
        self.assertEqual(str(c), '(a | b | <lambda>)')
        self.assertEqual(repr(c), f'FunctionChain({(a,b,l)})')

    def test_call(self):
        c = FunctionChain((a, b, l))
        self.assertEqual(c('_'), '_abl')


def a(x):
    return x + 'a'
def b(x):
    return x + 'b'
l = lambda x: x + 'l'
