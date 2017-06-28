import operator
import os

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions import concurrent
from metafunctions.exceptions import ConcurrentException


class TestUnit(BaseTestCase):
    def test_basic(self):
        ab = a + b
        cab = concurrent.ConcurrentMerge(ab)
        self.assertEqual(cab('_'), '_a_b')

    def test_exceptions(self):
        @node
        def fail(x):
            if not x:
                1 / 0
            return x - 1

        cmp = concurrent.ConcurrentMerge(fail - fail)

        with self.assertRaises(ConcurrentException) as e:
            cmp(0)
        self.assertIsInstance(e.exception.__cause__, ZeroDivisionError)
        self.assertEqual(e.exception.__cause__.args[0],
                'division by zero \n\n Occured in the following function: concurrent(->fail<- - fail)')

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

        cmp = concurrent.ConcurrentMerge(h + f + f / h + i - g)
        self.assertEqual(cmp(1), 3)
        # how do pretty tracebacks work in multiprocessing?

    def test_concurrent(self):
        #concurrent is a function that recursively upgrades merges
        self.fail('wip')

    def test_str_repr(self):
        cab = concurrent.ConcurrentMerge(a + b)

        self.assertEqual(repr(cab), f'ConcurrentMerge({operator.add}, ({repr(a)}, {repr(b)}))')
        self.assertEqual(str(cab), f'concurrent(a + b)')

### Simple Sample Functions ###
@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
