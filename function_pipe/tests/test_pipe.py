import operator

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

    def test_advanced_str(self):
        cmp = a | b + c + d | e
        self.assertEqual(str(cmp), '(a | ((b + c) + d) | e)')
        self.assertEqual(cmp('_'), '_ab_ac_ade')

    def test_non_callable_composition(self):
        '''Anything that is not callable in a composition is applied at call time (to the results
        of the composed functions).
        '''
        @pipe_node
        def g(x):
            return x

        cmps_to_expected = (
            (g + 1, 11),
            (g - 1, 9),
            (g * 2, 20),
            (g / 2, 5),
        )

        for cmp, expected in cmps_to_expected:
            with self.subTest():
                self.assertEqual(cmp(10), expected)


    def test_or(self):
        '''Assert that we can still use or'''
        @pipe_node
        def return_a_set(x):
            return set(*x)

        #Just wrap anything that isn't callable in a lambda, to put it off until call time
        outer_set = set((1, 2, 3))

        cmp = return_a_set | outer_set
        reverse_cmp = outer_set | return_a_set

        self.assertSetEqual(cmp('abc'), set('abc'))
        self.assertSetEqual(reverse_cmp('abc'), set('abc'))


    def test_single_calls(self):
        '''every function is only called once'''
        call_count = 0
        @pipe_node
        def y(x):
            nonlocal call_count
            call_count += 1
            return x + 'y'

        cmp = y | y * 2 | y + y | y
        self.assertEqual(cmp('_'), '_yyyyy')
        self.assertEqual(call_count, 5)

    def test_repr(self):
        cmp = a | b | c | (lambda x: None)
        self.assertEqual(str(cmp), '(a | b | c | <lambda>)')


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
@pipe_node
def e(x):
    return x + 'e'
