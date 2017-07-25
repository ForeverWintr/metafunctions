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

        @star
        def h(*x):
            return x

        cmp = (a | b) | star(f)
        star_a = star(a)
        merge_star = star(a+b)
        chain_star = star(a|b)

        self.assertEqual(str(cmp), '(a | b | star(f))')
        self.assertEqual(str(star_a), 'star(a)')
        self.assertEqual(str(g), 'star(g)')
        self.assertEqual(str(merge_star), 'star(a + b)')
        self.assertEqual(str(chain_star), 'star(a | b)')

        #You can technically apply star to a regular function, and it'll become a SimpleFunction
        self.assertEqual(str(h), f'star({h._function.__closure__[0].cell_contents})')

        #reprs remain the same
        self.assertEqual(repr(star_a), f'SimpleFunction({star_a._function})')


@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
