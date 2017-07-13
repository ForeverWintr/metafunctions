
from metafunctions.util import node
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_broadcast(self):
        @node
        def f(*args):
            return args

        cmp = (a | b) @ f
        self.assertEqual(cmp('_'), ('_', 'a', 'b'))

    def test_str_repr(self):
        c = a @ b
        self.assertEqual(str(c), '(a @ b)')
        self.assertEqual(repr(c), f"BroadcastChain{(a, b)}")

        c = a | a @ b * 5 / 7 | b & b @ a
        self.assertEqual(str(c), '(a | (((a @ b) * 5) / 7) | (b & (b @ a)))')

        c = (1, 2, 3) @ a
        self.assertEqual(str(c), '((1, 2, 3) @ a)')



@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
