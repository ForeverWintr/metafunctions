from unittest import mock
import functools

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import store, recall, node, highlight_current_function, bind_call_state
from metafunctions.core import MetaFunction, SimpleFunction, CallState


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

    def test_highlight_current_function(self):
        fmt_index = 6

        @node
        def ff(x):
            return x + 'F'

        @node
        @bind_call_state
        def f(call_state, x):
            if len(call_state._called_functions) == 6:
                location_string = highlight_current_function(call_state, use_color=False)
                location_string_color = highlight_current_function(call_state, use_color=True)
                self.assertEqual(location_string, '(a | b | ff | f | f | ->f<- | f | f)')
                self.assertEqual(location_string_color,
                        '(a | b | ff | f | f | \x1b[31m->f<-\x1b[0m | f | f)')
                self.assertEqual(x, '_abFff')
            return x + 'f'

        pipe = a | b | ff | f | f | f | f | f
        pipe('_')

        state = CallState()
        af = a + f
        af('_', call_state=state)
        curr_f = highlight_current_function(state, use_color=False)
        self.assertEqual(curr_f, '(a + ->f<-)')

    @mock.patch('metafunctions.util.highlight_current_function')
    def test_highlight_current_function_multichar(self, mock_h):
        mock_h.side_effect = functools.partial(highlight_current_function, use_color=False)
        # Don't fail on long named functions. This is a regression test
        @node
        def fail(x):
            if not x:
                1 / 0
            return x - 1

        cmp = fail | fail + a

        with self.assertRaises(ZeroDivisionError) as e:
            cmp(1)
        self.assertTrue(e.exception.args[0].endswith('(fail | (->fail<- + a))'))


@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
