import unittest

from metafunctions.util import node
from metafunctions.util import star
from metafunctions.util import concurrent
from metafunctions.operators import concat
from metafunctions.tests.util import BaseTestCase

class TestUnit(BaseTestCase):

    ## Interface tests
    def test_upgrade_merge(self):
        aabbcc = (a & b & c) @ (a&b&c)
        self.assertEqual(aabbcc('_'), ('_aa', '_bb', '_cc'))

    @unittest.skip('TODO')
    def test_recursive_upgrade(self):
        aabbcc = (a & b & c) @ star(a+b+c)
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')

    def test_str_repr(self):
        cmp = a @ (b&c)
        self.assertEqual(str(cmp), '(a | star(b & c))')
        self.assertEqual(repr(cmp),
                f'FunctionChain({a!r}, SimpleFunction({cmp._functions[1]._function}))')

    @unittest.skip('Map')
    def test_loop(self):
        cmp = (b & c & 'stoke') @ star(a)
        self.assertEqual(cmp('_'), ('_ba', '_ca', 'stokea'))

    @unittest.skip('Map')
    def test_loop_with_non_meta(self):
        cmp = (b & c & 'stoke') @ star(len)
        self.assertEqual(cmp('_'), (2, 2, 5))






### Simple Sample Functions ###
@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
@node
def c(x):
    return x + 'c'

