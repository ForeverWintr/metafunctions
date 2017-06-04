
from function_pipe.tests.util import BaseTestCase
from function_pipe.decorators import pipe_node



class TestUnit(BaseTestCase):
    def test_basic_usage(self):
        self.assertEqual(a('_'), '_a')

    def test_wraps(self):
        @pipe_node
        def d():
            'a docstring for d'
        self.assertEqual(d.__doc__, 'a docstring for d')

    def test_auto_meta(self):
        '''If possible, we upgrade functions to meta functions on the fly.'''
        def y(x):
            return x + 'y'

        ay = a | y
        ya = y | a

        self.assertEqual(ay('_'), '_ay')
        self.assertEqual(ya('_'), '_ya')

    def test_basic_composition(self):
        composite = a | b | c | d
        self.assertEqual(composite('_'), '_abcd')


### Simple Sample Functions ###
@pipe_node
def a(x):
    return x + 'a'
@pipe_node
def b(x):
    return x + 'b'
@pipe_node
def c(x):
    return x + 'c'
@pipe_node
def d(x):
    return x + 'd'
