import operator
import os

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions import concurrent
from metafunctions.exceptions import ConcurrentException


class TestIntegration(BaseTestCase):
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


        # how do pretty tracebacks work in multiprocessing?

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
