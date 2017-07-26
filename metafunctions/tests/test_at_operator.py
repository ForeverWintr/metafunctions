import unittest

from metafunctions.util import node
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_broadcast(self):
        @node
        def f(*args):
            return args

        cmp = (a | b) @ f
        self.assertEqual(cmp('_'), ('_', 'a', 'b'))

        rcmp = (1, 2, 3) @ f
        self.assertEqual(rcmp(), (1, 2, 3))

    def test_str_repr(self):
        c = a @ b
        self.assertEqual(str(c), '(a | star(b))')
        self.assertEqual(repr(c),
                f"FunctionChain{(a, c.functions[1])}")

        c = a | a @ b * 5 / 7 | b & b @ a
        self.assertEqual(str(c), '(a | (((a | star(b)) * 5) / 7) | (b & (b | star(a))))')

        c = (1, 2, 3) @ a
        self.assertEqual(str(c), '((1, 2, 3) | star(a))')

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

@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'

@node
def c(x):
    return x + 'c'

