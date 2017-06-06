import operator

from function_pipe.metafunctions import FunctionChain
from function_pipe.metafunctions import FunctionMerge
from function_pipe.metafunctions import SimpleFunction
from function_pipe.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_str(self):
        c = FunctionChain((a, b, l))
        self.assertEqual(str(c), '(a | b | <lambda>)')
        self.assertEqual(repr(c), f'FunctionChain({(a,b,l)})')

    def test_call(self):
        c = FunctionChain((a, b, l))
        self.assertEqual(c('_'), '_abl')

    def test_combine(self):
        '''Avoid nesting chains'''
        chain = FunctionChain((a, b, l))
        merge = FunctionMerge(operator.add, (a, b))

        self.assertEqual(str(FunctionChain.combine(chain, chain)),
                '(a | b | <lambda> | a | b | <lambda>)')
        self.assertEqual(str(chain|chain),
                '(a | b | <lambda> | a | b | <lambda>)')
        self.assertEqual(str(chain | merge | chain),
                '(a | b | <lambda> | (a + b) | a | b | <lambda>)')

@SimpleFunction
def a(x):
    return x + 'a'
@SimpleFunction
def b(x):
    return x + 'b'
l = SimpleFunction(lambda x: x + 'l')
