from metafunctions.api import node
from metafunctions.tests.util import BaseTestCase
from metafunctions.tests.simple_nodes import *


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
        cmp = a @ b
        self.assertEqual(str(cmp), '(a | star(b))')
        self.assertEqual(repr(cmp),
                "FunctionChain{}".format((a, cmp.functions[1])))

        cmp = a | a @ b * 5 / 7 | b & b @ a
        self.assertEqual(str(cmp), '(a | (((a | star(b)) * 5) / 7) | (b & (b | star(a))))')

        cmp = (1, 2, 3) @ a
        self.assertEqual(str(cmp), '((1, 2, 3) | star(a))')

        cmp = a @ (b&c)
        self.assertEqual(str(cmp), '(a | star(b & c))')
        self.assertEqual(repr(cmp),
            'FunctionChain({0!r}, SimpleFunction({1}))'.format(a, cmp._functions[1]._function))

    def test_upgrade_merge(self):
        aabbcc = (a & b & c) @ (a&b&c)
        self.assertEqual(aabbcc('_'), ('_aa', '_bb', '_cc'))


