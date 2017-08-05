from unittest import mock
import functools

from metafunctions.tests.util import BaseTestCase
from metafunctions.api import store, recall, node, bind_call_state
from metafunctions.util import highlight_current_function
from metafunctions.core import SimpleFunction, CallState


class TestUnit(BaseTestCase):
    def test_bind_call_state(self):
        '''
        If decorated with bind_call_state, the function receives the call state dictionary as its
        first argument.
        '''
        @node
        @bind_call_state
        def a_(call_state, x):
            self.assertIsInstance(call_state, CallState)
            call_state.data['a'] = 'b'
            return x + 'a'
        @node
        @bind_call_state
        def f(call_state, x):
            return x + call_state.data.get('a', 'f')

        self.assertEqual(a('_'), '_a')
        self.assertEqual(f('_'), '_f')

        cmp = a_ | f
        self.assertEqual(cmp('_'), '_ab')
        cmp = f | a_ | a_ | f + f
        self.assertEqual(cmp('_'), '_faab_faab')

    def test_node_bracketless(self):
        '''
        I'm allowing the node decorator to be applied without calling because this is how both
        celery and function_pipes work.
        '''
        @node
        def a(x):
            return x + 'a'
        @node()
        def b(x):
            return x + 'b'

        self.assertIsInstance(a, SimpleFunction)
        self.assertIsInstance(b, SimpleFunction)
        self.assertEqual((b|a)('_'), '_ba')

    def test_store(self):
        state = CallState()
        abc = a | b | store('output') | c
        big = (a | b | c + store('ab') + store('ab2') | store('abc') | recall('ab') + recall('ab2') |
               c + recall('abc'))

        self.assertEqual(abc('_', call_state=state), '_abc')
        self.assertEqual(state.data['output'], '_ab')
        self.assertEqual(big('_'), '_ab_abc_abc_ab_ab')

    def test_recall(self):
        state = a.new_call_state()
        state.data['k'] = 'secret'

        cmp = a + b | store('k') | c + recall('k')
        self.assertEqual(cmp('_'), '_a_bc_a_b')

        cmp = a + b | store('k') | c + recall('k') | recall('k', from_call_state=state)
        self.assertEqual(cmp('_'), 'secret')

    def test_str_store(self):
        #this should be possible
        self.assertEqual(str(store('key')), "store('key')")

    def test_str_recall(self):
        self.assertEqual(str(recall('key')), "recall('key')")


@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
