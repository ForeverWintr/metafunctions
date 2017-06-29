import operator
import os
from unittest import mock
import functools

import colors

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions.util import highlight_current_function
from metafunctions.util import concurrent
from metafunctions.concurrent import ConcurrentMerge
from metafunctions.exceptions import ConcurrentException


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
        @node(bind=True)
        def f(meta, x):
            self.assertIs(meta, cmp)
            return 1
        @node(bind=True)
        def g(meta, x):
            self.assertIs(meta, cmp)
            return 1
        @node(bind=True)
        def h(meta, x):
            self.assertIs(meta, cmp)
            return 1
        @node(bind=True)
        def i(meta, x):
            self.assertIs(meta, cmp)
            return 1

        cmp = ConcurrentMerge(h + f + f / h + i - g)
        self.assertEqual(cmp(1), 3)
        # how do pretty tracebacks work in multiprocessing?

    def test_concurrent(self):
        c = concurrent(a + b)
        self.assertIsInstance(c, ConcurrentMerge)
        self.assertEqual(c('_'), '_a_b')

    def test_str_repr(self):
        cab = ConcurrentMerge(a + b)

        self.assertEqual(repr(cab), f'ConcurrentMerge({operator.add}, ({repr(a)}, {repr(b)}))')
        self.assertEqual(str(cab), f'concurrent(a + b)')

### Simple Sample Functions ###
@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
