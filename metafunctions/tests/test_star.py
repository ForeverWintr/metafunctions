import unittest
import os

from metafunctions.api import node, star, concurrent
from metafunctions.tests.simple_nodes import *
from metafunctions import exceptions
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_simple_star(self):
        @node
        def f(*args):
            return args

        cmp = (a | b) | star(f)
        self.assertEqual(cmp('_'), ('_', 'a', 'b'))

        self.assertEqual(star(f)([1, 2, 3]), (1, 2, 3))

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
        self.assertEqual(str(h), 'star({})'.format(h._function.__closure__[0].cell_contents))

        #reprs remain the same
        self.assertEqual(repr(star_a), 'SimpleFunction({})'.format(star_a._function))

    @unittest.skipUnless(hasattr(os, 'fork'), "Concurent isn't available on windows")
    def test_concurrent(self):
        # Concurrent and star can work together, although this organization no longer makes sense
        with self.assertRaises(exceptions.CompositionError):
            aabbcc = a & b & c | concurrent(star(a&b&c))
        #self.assertEqual(aabbcc('_'), '_aa_bb_cc')

        aabbcc = (a & b & c) | star(concurrent(a&b&c))
        self.assertEqual(aabbcc('_'), ('_aa','_bb','_cc'))

    @unittest.skip('TODO')
    def test_recursive_upgrade(self):
        aabbcc = (a & b & c) | star(a+b+c)
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')

