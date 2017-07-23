from metafunctions.util import node, star
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_simple_star(self):
        @node
        def f(*args):
            return args

        cmp = (a | b) | star(f)
        self.assertEqual(cmp('_'), ('_', 'a', 'b'))

    def test_str_repr(self):
        @node
        def f(*args):
            return args

        @star
        @node
        def g(*x):
            return x

        @node
        @star
        def h(*x):
            return x

        cmp = (a | b) | star(f)
        star_a = star(a)

        self.assertEqual(str(cmp), '(a | b | star(f))')
        self.assertEqual(str(star_a), 'star(a)')
        self.assertEqual(str(g), 'star(g)')
        self.assertEqual(str(h), 'h')

@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
