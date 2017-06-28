import operator
import os

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions import concurrent


class TestIntegration(BaseTestCase):
    def test_basic(self):
        ab = a + b
        cab = concurrent.ConcurrentMerge(ab)

        #try:
        self.assertEqual(cab('_'), '_a_b')
        #except SystemExit:
            ##child processes call systemexit. Stop the test suite from freaking out about it here
            #os._exit(0)
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
