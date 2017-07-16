
from metafunctions.util import node
from metafunctions.util import star
from metafunctions.util import concurrent
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_upgrade_merge(self):
        aabbcc = a & b & c @ star(a+b+c)
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')

    def test_str_repr(self):
        cmp = a @ star(b&c)
        self.assertEqual(str(cmp), '(a @ star(b & c))')
        self.assertEqual(repr(cmp), 'something')

    def test_loop(self):
        cmp = (b & c & 'stoke') @ star(a)
        self.assertEqual(cmp('_'), ('_ba', '_ca', '_stokea'))

    def test_concurrent(self):
        # Concurrent and star can work together
        aabbcc = a & b & c @ concurrent(star(a+b+c))
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')

        # order of application doesn't matter
        aabbcc = a & b & c @ star(concurrent(a+b+c))
        self.assertEqual(aabbcc('_'), '_aa_bb_cc')



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

