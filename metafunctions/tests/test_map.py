
from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions.util import star
from metafunctions.util import mmap
from metafunctions.map import MergeMap
from metafunctions import operators

class TestIntegration(BaseTestCase):
    def test_basic(self):
        banana = 'bnn' | MergeMap(a) | ''.join
        str_concat = operators.concat | node(''.join)
        batman = MergeMap(a, merge_function=str_concat)
        self.assertEqual(banana(), 'banana')
        self.assertEqual(batman('nnnn'), 'nananana')

    def test_multi_arg(self):
        @node
        def f(*args):
            return args

        m = mmap(f)
        starmap = star(mmap(f))
        mapstar = mmap(star(f))

        self.assertEqual(m([1, 2, 3], [4, 5, 6]), ((1, 4), (2, 5), (3, 6)))
        self.assertEqual(m([1, 2, 3]), ((1, ), (2, ), (3, )))

        with self.assertRaises(TypeError):
            self.assertEqual(starmap([1, 2, 3]))
        self.assertEqual(starmap([[1, 2, 3]]), m([1, 2, 3]))

        cmp = ([1, 2, 3], [4, 5, 6]) | starmap
        self.assertEqual(cmp(), ((1, 4), (2, 5), (3, 6)))

        cmp = ([1, 2, 3], [4, 5, 6]) | mapstar
        self.assertEqual(cmp(), ((1, 2, 3), (4, 5, 6)))

    def test_str_repr(self):
        m = MergeMap(a)
        self.assertEqual(str(m), 'mmap(a)')
        self.assertEqual(repr(m), f'MergeMap')


@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
@node
def c(x):
    return x + 'c'
