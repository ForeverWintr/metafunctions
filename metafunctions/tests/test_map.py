
from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions.map import MergeMap
from metafunctions import operators

class TestIntegration(BaseTestCase):
    def test_basic(self):
        banana = 'bnn' | MergeMap(a)
        batman = 'bnn' | MergeMap(a, merge_function=operators.add)
        self.assertEqual(banana(), 'banana')

    def test_str_repr(self):
        m = MergeMap(a)
        self.assertEqual(str(m), '')
        self.assertEqual(repr(m), '')


@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
@node
def c(x):
    return x + 'c'
