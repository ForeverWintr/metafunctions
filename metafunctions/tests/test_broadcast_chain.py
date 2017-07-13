
from metafunctions.util import node
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_split(self):
        @node
        def f(*args):
            return args

        cmp = (a | b) @ f
        self.assertEqual(cmp('_'), ('_', 'a', 'b'))

    def test_str_repr(self):
        c = a @ b
        self.assertEqual(str(c), '(a @ b)')
        self.assertEqual(repr(c), f"BroadcastChain{(a, b)}")


@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
