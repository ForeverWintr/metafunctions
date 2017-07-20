
from metafunctions.tests.util import BaseTestCase
from metafunctions.util import bind_call_state
from metafunctions.util import node
from metafunctions.core import CallState


class TestUnit(BaseTestCase):
    def test_bind_call_state(self):
        # Bound functions receive call state
        @node
        @bind_call_state
        def f(call_state, x):
            self.assertIsInstance(call_state, CallState)
            call_state.data['h'] = 'b'
            return x + 'f'

        @node
        def g(x):
            return x + 'g'

        @node
        @bind_call_state
        def h(call_state, x):
            self.assertIsInstance(call_state, CallState)
            return x + call_state.data['h']

        fg = f | g | h
        self.assertEqual(fg('_'), '_fgb')

    def test_provide_call_state(self):
        # A call state you provide is passed to all functions
        @node
        @bind_call_state
        def f(call_state, x):
            self.assertIs(call_state, c)
            call_state.data['h'] = 'd'
            return x + 'f'
        @node
        def g(x):
            return x + 'g'
        @node
        @bind_call_state
        def h(call_state, x):
            self.assertIs(call_state, c)
            return x + call_state.data['h']
        fg = f | g | h

        c = CallState()
        self.assertEqual(fg('_', call_state=c), '_fgd')

