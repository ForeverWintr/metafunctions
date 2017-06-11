import unittest

from metafunctions.tests.util import BaseTestCase
from metafunctions.decorators import node


class TestIntegration(BaseTestCase):
    def test_basic_usage(self):
        self.assertEqual(a('_'), '_a')

    def test_wraps(self):
        @node
        def d():
            'a docstring for d'
        self.assertEqual(d.__doc__, 'a docstring for d')

    def test_auto_meta(self):
        '''If possible, we upgrade functions to meta functions on the fly.'''
        def y(x):
            return x + 'y'

        ay = a | y
        ya = y | a
        ayyyy = a | y | y | y | y

        # Can't do this
        #ayy = a | y + y

        # But this should work
        yayy = y | a + y
        yy_ya = y | y + a

        self.assertEqual(ay('_'), '_ay')
        self.assertEqual(ya('_'), '_ya')
        self.assertEqual(ayyyy('_'), '_ayyyy')
        self.assertEqual(yayy('_'), '_ya_yy')
        self.assertEqual(yy_ya('_'), '_yy_ya')

    def test_auto_meta_builtins(self):
        '''We can upgrade builtin functions too'''

        mean = node(sum) / len
        self.assertEqual(mean((100, 200, 300)), 200)

    def test_basic_composition(self):
        composite = a | b | c | d
        self.assertEqual(composite('_'), '_abcd')

    def test_advanced_str(self):
        cmp = a | b + c + d | e
        self.assertEqual(str(cmp), '(a | ((b + c) + d) | e)')
        self.assertEqual(cmp('_'), '_ab_ac_ade')

        cmp = a + 'f'
        self.assertEqual(str(cmp), "(a + 'f')")

    def test_non_callable_composition(self):
        '''
        Anything that is not callable in a composition is applied at call time (to the results
        of the composed functions).
        '''
        @node
        def g(x):
            return x

        cmps_to_expected = (
            (g + 1, 11),
            (g - 1, 9),
            (g * 2, 20),
            (g / 2, 5),
            (1 + g, 11),
            (1 - g, -9),
            (2 * g, 20),
            (2 / g, .2),
        )

        for cmp, expected in cmps_to_expected:
            with self.subTest():
                self.assertEqual(cmp(10), expected)

    @unittest.skip("Making this work doesn't make sense anymore")
    def test_or(self):
        '''Assert that we can still use or'''
        @node
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
        @node
        def y(x):
            nonlocal call_count
            call_count += 1
            return x + 'y'

        cmp = y | y * 2 | y + y | y
        self.assertEqual(cmp('_'), '_yy_yyy_yy_yyyy')
        self.assertEqual(call_count, 5)

    def test_repr(self):
        cmp = a | b | c | (lambda x: None)
        self.assertEqual(str(cmp), '(a | b | c | <lambda>)')


### Simple Sample Functions ###
@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
@node
def c(x):
    return x + 'c'
@node
def d(x):
    return x + 'd'
@node
def e(x):
    return x + 'e'
