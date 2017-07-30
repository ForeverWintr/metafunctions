import operator
import os
from unittest import mock
import functools

import colors

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions.util import bind_call_state
from metafunctions.util import highlight_current_function
from metafunctions.util import concurrent
from metafunctions.util import mmap
from metafunctions.concurrent import ConcurrentMerge
from metafunctions import operators
from metafunctions.exceptions import ConcurrentException, CompositionError, CallError


class TestUnit(BaseTestCase):
    def test_basic(self):
        ab = a + b
        cab = ConcurrentMerge(ab)
        self.assertEqual(cab('_'), '_a_b')

    @mock.patch('metafunctions.util.highlight_current_function')
    def test_exceptions(self, mock_h):
        mock_h.side_effect = functools.partial(highlight_current_function, use_color=True)
        @node
        def fail(x):
            if not x:
                1 / 0
            return x - 1

        cmp = ConcurrentMerge(fail - fail)

        with self.assertRaises(ConcurrentException) as e:
            cmp(0)
        self.assertIsInstance(e.exception.__cause__, ZeroDivisionError)
        self.assertEqual(e.exception.__cause__.args[0],
                f'division by zero \n\nOccured in the following function: '
                f'concurrent({colors.red("->fail<-")} - fail)')

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

        cmp = ConcurrentMerge(h + f + f / h + i - g)
        self.assertEqual(cmp(1), 3)

        self.assertEqual(cmp(1, call_state=cmp.new_call_state()), 3)

        # how do pretty tracebacks work in multiprocessing?

    def test_call(self):
        c = concurrent(a+b)
        self.assertEqual(c('_'), '_a_b')
        self.assertEqual(c('-', '_'), '-a_b')
        with self.assertRaises(CallError):
            c('_', '_', '_')

        @node
        def d():
            return 'd'
        abd = concurrent(a & b & d)
        self.assertEqual(abd('-', '_'), ('-a', '_b', 'd'))

    def test_concurrent(self):
        c = concurrent(a + b)
        self.assertIsInstance(c, ConcurrentMerge)
        self.assertEqual(c('_'), '_a_b')

    def test_not_concurrent(self):
        #can only upgrade FunctionMerges

        with self.assertRaises(CompositionError):
            concurrent(a)
        with self.assertRaises(CompositionError):
            concurrent(a | b)

    def test_str_repr(self):
        cab = ConcurrentMerge(a + b)

        self.assertEqual(repr(cab), f'ConcurrentMerge({operator.add}, ({repr(a)}, {repr(b)}))')
        self.assertEqual(str(cab), f'concurrent(a + b)')

    def test_basic_map(self):
        # We can upgrade maps to run in parallel
        banana = 'bnn' | concurrent(mmap(a)) | ''.join
        str_concat = operators.concat | node(''.join)
        batman = concurrent(mmap(a, operator=str_concat))
        self.assertEqual(banana(), 'banana')
        self.assertEqual(batman('nnnn'), 'nananana')

### Simple Sample Functions ###
@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
