import operator

from metafunctions.core import FunctionMerge
from metafunctions.core import SimpleFunction
from metafunctions.tests.util import BaseTestCase
from metafunctions.operators import concat
from metafunctions import exceptions


class TestUnit(BaseTestCase):
    def test_str(self):
        c = FunctionMerge(operator.add, (a, b))
        self.assertEqual(str(c), '(a + b)')
        self.assertEqual(repr(c), f'FunctionMerge({operator.add}, {(a, b)})')

    def test_call(self):
        c = FunctionMerge(operator.add, (a, b))
        self.assertEqual(c('_'), '_a_b')
        self.assertEqual(c('-', '_'), '-a_b')
        with self.assertRaises(exceptions.CallError):
            c('_', '_', '_')

        @SimpleFunction
        def d():
            return 'd'
        abd = a & b & d
        self.assertEqual(abd('-', '_'), ('-a', '_b', 'd'))


    def test_format(self):
        c = FunctionMerge(operator.add, (a, b), function_join_str='tacos')
        self.assertEqual(str(c), '(a tacos b)')

    def test_non_binary(self):
        def concat(*args):
            return ''.join(args)

        c = FunctionMerge(concat, (a, a, a, a))
        self.assertEqual(c('_'), '_a_a_a_a')

        self.assertEqual(str(c), f'(a {concat} a {concat} a {concat} a)')

        d = FunctionMerge(concat, (b, b), function_join_str='q')
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

        def concat(*args):
            return ''.join(args)
        bb = FunctionMerge(concat, (b, b), function_join_str='q')
        aa = FunctionMerge(concat, (a, a), function_join_str='q')
        bbaa = FunctionMerge.combine(concat, bb, aa, function_join_str='q')
        self.assertEqual(str(bbaa), '(b q b q a q a)')
        self.assertEqual(repr(bbaa), f"FunctionMerge({concat}, {(b, b, a, a)})")


@SimpleFunction
def a(x):
    return x + 'a'
@SimpleFunction
def b(x):
    return x + 'b'
l = SimpleFunction(lambda x: x + 'l')
