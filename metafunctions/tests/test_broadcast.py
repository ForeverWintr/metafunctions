import unittest

from metafunctions.util import node
from metafunctions.util import star
from metafunctions.util import concurrent
from metafunctions.operators import concat
from metafunctions.exceptions import BroadcastError
from metafunctions.tests.util import BaseTestCase

@unittest.skip('TODO')
class TestUnit(BaseTestCase):

    ## Interface tests
    def test_upgrade_merge(self):
        aabbcc = (a & b & c) @ star(a&b&c)
        self.assertEqual(aabbcc('_'), ('_aa', '_bb', '_cc'))

    @unittest.skip('TODO')
    def test_recursive_upgrade(self):
        aabbcc = (a & b & c) @ star(a+b+c)
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')

    def test_str_repr(self):
        cmp = a @ star(b&c)
        self.assertEqual(str(cmp), '(a @ star(b & c))')
        self.assertEqual(repr(cmp), f'BroadcastChain({a!r}, BroadcastMerge({concat}, {(b,c)}))')

    def test_loop(self):
        cmp = (b & c & 'stoke') @ star(a)
        self.assertEqual(cmp('_'), ('_ba', '_ca', 'stokea'))

    def test_loop_with_non_meta(self):
        cmp = (b & c & 'stoke') @ star(len)
        self.assertEqual(cmp('_'), (2, 2, 5))

    def test_concurrent(self):
        # Concurrent and star can work together
        aabbcc = a & b & c @ concurrent(star(a+b+c))
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')

        # order of application doesn't matter
        aabbcc = a & b & c @ star(concurrent(a+b+c))
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')

    ## Implementation tests
    def test_len_mismatch(self):
        # If len(inputs) <= len(functions), call remaining functions with `None`.
        @node
        def f(x=None):
            if x:
                return x + 'f'
            return 'F'

        cmp = (a & b) @ star(f&f&f&f)
        self.assertEqual(cmp('_'), ('_af', '_bf', 'F', 'F'))

        # if len(functions) == 1, call function once per input.
        cmp = (a & b) @ star(f)
        self.assertEqual(cmp('_'), ('_af', '_bf'))

        # if len(inputs) > len(functions), fail.
        cmp = (a & b & c) @ star(f+f)
        with self.assertRaises(BroadcastError):
            cmp('_')

        #TODO: Using pipe instead of broadcast has the potential to be confusing. This passes (a,
        #b) to the first f
        cmp = (a & b) | star(f+f)
        with self.assertRaises(TypeError):
            cmp('_')

    @unittest.skip('TODO')
    def test_binary_functions(self):
        # The issue here is that f + f + f + f is not converted to a single FunctionMerge. Rather
        # it becomes nested FunctionMerges: (((f + f) + f) + f). Ideally star would be able to
        # handle this. One potential solution is to 'flatten' the FunctionMerge, but this doesn't
        # work for functions that aren't commutative. E.g., (a / b / c) != (a / (b / c)). I'm
        # leaving this test for now as a todo.
        @node
        def f(x=None):
            if x:
                return x + 'f'
            return 'F'

        cmp = (a & b) @ star(f+f+f+f)
        self.assertEqual(cmp('_'), '_af_bfFF')


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

