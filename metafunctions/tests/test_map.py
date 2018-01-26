
from metafunctions.tests.util import BaseTestCase
from metafunctions.tests.simple_nodes import *
from metafunctions.api import node
from metafunctions.api import star
from metafunctions.api import mmap
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
            starmap([1, 2, 3])
        self.assertEqual(starmap([[1, 2, 3]]), m([1, 2, 3]))

        cmp = ([1, 2, 3], [4, 5, 6]) | starmap
        self.assertEqual(cmp(), ((1, 4), (2, 5), (3, 6)))

        cmp = ([1, 2, 3], [4, 5, 6]) | mapstar
        self.assertEqual(cmp(), ((1, 2, 3), (4, 5, 6)))

    def test_auto_meta(self):
        mapsum = mmap(sum)
        self.assertEqual(mapsum([[1, 2], [3, 4]]), (3, 7))
        self.assertEqual(str(mapsum), 'mmap(sum)')

    def test_str_repr(self):
        m = MergeMap(a)
        self.assertEqual(str(m), 'mmap(a)')
        self.assertEqual(repr(m), 'MergeMap(a, merge_function={})'.format(operators.concat))

    def test_loop(self):
        cmp = (b & c & 'stoke') | mmap(a)
        self.assertEqual(cmp('_'), ('_ba', '_ca', 'stokea'))

    def test_loop_with_non_meta(self):
        cmp = (b & c & 'stoke') | mmap(len)
        self.assertEqual(cmp('_'), (2, 2, 5))


