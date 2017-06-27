import operator

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions import concurrent


class TestIntegration(BaseTestCase):
    def test_basic(self):
        ab = a + b
        cab = concurrent.ConcurrentMerge(ab)

        self.assertEqual(cab('_'), '_ab')
        self.fail()
        # how do pretty tracebacks work in multiprocessing?

    def test_str_repr(self):
        cab = concurrent.ConcurrentMerge(a + b)

        self.assertEqual(repr(cab), f'ConcurrentMerge({operator.add}, ({repr(a)}, {repr(b)}))')
        self.assertEqual(str(cab), f'parallel(a + b)')

### Simple Sample Functions ###
@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
