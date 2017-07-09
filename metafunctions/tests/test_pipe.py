import unittest
from unittest import mock
import functools

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions.util import bind_call_state
from metafunctions.util import highlight_current_function
from metafunctions.core import CallState


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
        self.assertEqual(repr(cmp),
                "FunctionMerge(<built-in function add>, "
                f"(SimpleFunction({repr(a._function)}), DeferredValue('f')))")

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

    def test_called_functions(self):
        '''
        Parent refers to the parent MetaFunction.
        '''

        @node
        @bind_call_state
        def parent_test(call_state, x):
            return call_state

        ab = a | b
        abc = ab + c
        abc_ = abc | parent_test

        call_state = abc_('_')
        self.assertIsInstance(call_state, CallState)
        self.assertListEqual(call_state._called_functions, [a, b, c, parent_test])

    @mock.patch('metafunctions.util.highlight_current_function')
    def test_pretty_exceptions(self, mock_h):
        mock_h.side_effect = functools.partial(highlight_current_function, use_color=False)

        @node
        def f(x):
            raise RuntimeError('Something bad happened!')
        @node(modify_tracebacks=False)
        def g(x):
            raise RuntimeError('Something bad happened in g!')

        abf = a | b + f
        abg = a | b + g

        with self.assertRaises(RuntimeError) as ctx:
            # TODO: assert that tracebacks are correct
            abf('_')

        self.assertEqual(str(ctx.exception),
                'Something bad happened! \n\nOccured in the following function: (a | (b + ->f<-))')

        # unprettified exceptions work
        with self.assertRaises(RuntimeError):
            abg('_')

    def test_consistent_meta(self):
        '''
        Every function in the pipeline recieves the same meta.
        '''
        @node
        @bind_call_state
        def f(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1
        @node()
        @bind_call_state
        def g(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1
        @node
        @bind_call_state
        def h(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1
        @node
        @bind_call_state
        def i(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1

        cmp = f | g | i | h + f + f / h + i - g
        self.assertEqual(cmp(1), 3)

        #this works if we provide our own call_state too.
        self.assertEqual(cmp(1, call_state=CallState()), 3)

    def test_defaults(self):
        '''
        If you specify defaults in nodes, they are respected.
        '''
        @node
        def f(x='F'):
            return x + 'f'
        @node()
        def g(meta, x='G'):
            return x + 'g'

        cmp = f | g | f + g
        self.assertEqual(cmp(), 'FfgfFfgg')
        self.assertEqual(cmp('_'), '_fgf_fgg')

        cmp2 = g | f | f + g
        self.assertEqual(cmp2(), 'GgffGgfg')
        self.assertEqual(cmp2('_'), '_gff_gfg')

    def test_complex_exceptions(self):
        @node
        def query_volume(x):
            return str(x ** 2)
        @node
        def query_price(x):
            return '$' + str(x ** 3)

        numeric = (query_volume | float) + (query_price | float)
        with self.assertRaises(ValueError) as e:
            numeric(2)

    def test_decoration(self):
        # It should be possible to decorate a metafunction with another metafunction and have
        # everything still work (as long as the decorated function gets upgraded to a metafunction.
        # consider a @metadecorator decorator to facilitate this).

        @node()
        def f(meta, x):
            self.assertIs(meta, abcf)
            return x + 'f'

        fn = node(f+'sup')
        abcf = a | b | c | fn

        self.assertEqual(abcf('_'), '_abcfsup')

    def test_kwargs(self):
        #Kwargs are passed to all functions

        @node
        def k(x, k='k'):
            return x + k

        self.assertEqual(k('_'), '_k')
        self.assertEqual(k('_', k='_'), '__')

        kk = k + k
        self.assertEqual(kk('_'), '_k_k')
        self.assertEqual(kk('_', k='_'), '____')

        klen = k | len
        self.assertEqual(klen('_'), 2)
        with self.assertRaises(TypeError):
            #passing a kwarg to len causes an error
            klen('_', k=5)

    def test_recursion(self):
        # Recursion should work with bind. how?
        self.fail('thinking')




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

