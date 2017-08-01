import operator
import unittest

from metafunctions.core import FunctionMerge
from metafunctions.core import SimpleFunction
from metafunctions.tests.util import BaseTestCase
from metafunctions.operators import concat
from metafunctions import exceptions
from metafunctions.util import node, star


class TestUnit(BaseTestCase):
    def test_str(self):
        cmp = FunctionMerge(operator.add, (a, b))
        self.assertEqual(str(cmp), '(a + b)')
        self.assertEqual(repr(cmp), f'FunctionMerge({operator.add}, {(a, b)})')

    def test_call(self):
        cmp = FunctionMerge(operator.add, (a, b))
        self.assertEqual(cmp('_'), '_a_b')
        self.assertEqual(cmp('-', '_'), '-a_b')
        with self.assertRaises(exceptions.CallError):
            cmp('_', '_', '_')

        @SimpleFunction
        def d():
            return 'd'
        abd = a & b & d
        self.assertEqual(abd('-', '_'), ('-a', '_b', 'd'))

    def test_format(self):
        cmp = FunctionMerge(operator.add, (a, b), function_join_str='tacos')
        self.assertEqual(str(cmp), '(a tacos b)')

    def test_non_binary(self):
        def my_concat(*args):
            return ''.join(args)

        cmp = FunctionMerge(my_concat, (a, a, a, a))
        self.assertEqual(cmp('_'), '_a_a_a_a')

        self.assertEqual(str(cmp), f'(a {my_concat} a {my_concat} a {my_concat} a)')

        d = FunctionMerge(my_concat, (b, b), function_join_str='q')
        self.assertEqual(str(d), '(b q b)')

    def test_join(self):
        # The first real non-binary function! Like the example above.

        cmp = a & a & 'sweet as'

        self.assertTupleEqual(cmp('_'), ('_a', '_a', 'sweet as'))
        self.assertEqual(str(cmp), "(a & a & 'sweet as')")
        self.assertEqual(repr(cmp), f"FunctionMerge({concat}, {(a, a, cmp._functions[-1])})")

        #__rand__ works too
        a_ = 'sweet as' & a
        self.assertEqual(a_('+'), ('sweet as', '+a'))

        abc = (a & (b & c)) | ''.join
        self.assertEqual(abc('_'), '_a_b_c')


    def test_combine(self):
        # Only combine FunctionMerges that have the same MergeFunc
        add = a + b
        also_add = b + a
        div = a / b

        #This combined FunctionMerge will fail if called (because addition is binary,
        #operator.add only takes two args). I'm just using to combine for test purposes.
        abba = FunctionMerge.combine(operator.add, add, also_add)
        self.assertEqual(str(abba), '(a + b + b + a)')
        self.assertEqual(repr(abba), f"FunctionMerge({operator.add}, {(a, b, b, a)})")

        ab_ba = FunctionMerge.combine(operator.sub, add, also_add)
        self.assertEqual(str(ab_ba), '((a + b) - (b + a))')
        self.assertEqual(repr(ab_ba), f"FunctionMerge({operator.sub}, {(add, also_add)})")

        abab = FunctionMerge.combine(operator.add, add, div)
        self.assertEqual(str(abab), '(a + b + (a / b))')
        self.assertEqual(repr(abab), f"FunctionMerge({operator.add}, {(a, b, div)})")

        def custom():
            pass
        abba_ = FunctionMerge.combine(custom, add, also_add, function_join_str='<>')
        self.assertEqual(str(abba_), '((a + b) <> (b + a))')
        self.assertEqual(repr(abba_), f"FunctionMerge({custom}, {(add, also_add)})")

        def my_concat(*args):
            return ''.join(args)
        bb = FunctionMerge(my_concat, (b, b), function_join_str='q')
        aa = FunctionMerge(my_concat, (a, a), function_join_str='q')
        bbaa = FunctionMerge.combine(my_concat, bb, aa, function_join_str='q')
        self.assertEqual(str(bbaa), '(b q b q a q a)')
        self.assertEqual(repr(bbaa), f"FunctionMerge({my_concat}, {(b, b, a, a)})")

    def test_len_mismatch(self):
        # If len(inputs) <= len(functions), call remaining functions with  no args.
        @node
        def f(x=None):
            if x:
                return x + 'f'
            return 'F'

        cmp = (a & b) | star(f&f&f&f)
        self.assertEqual(cmp('_'), ('_af', '_bf', 'F', 'F'))

        # if len(inputs) > len(functions), fail.
        cmp = (a & b & c) | star(f+f)
        with self.assertRaises(exceptions.CallError):
            cmp('_')

    @unittest.skip('TODO')
    def test_binary_functions(self):
        # The issue here is that f + f + f + f is not converted to a single FunctionMerge. Rather
        # it becomes nested FunctionMerges: (((f + f) + f) + f). Ideally we would be able to
        # handle this. One potential solution is to 'flatten' the FunctionMerge, but this doesn't
        # work for functions that aren't commutative. E.g., (a / b / c) != (a / (b / c)). I'm
        # leaving this test for now as a todo.
        @node
        def f(x=None):
            if x:
                return x + 'f'
            return 'F'

        cmp = (a & b) | star(f+f+f+f)
        self.assertEqual(cmp('_'), '_af_bfFF')


@SimpleFunction
def a(x):
    return x + 'a'
@SimpleFunction
def b(x):
    return x + 'b'
@node
def c(x):
    return x + 'c'
l = SimpleFunction(lambda x: x + 'l')
