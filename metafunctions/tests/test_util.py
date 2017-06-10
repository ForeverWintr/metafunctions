
import unittest

from metafunctions.tests.util import BaseTestCase
from metafunctions.decorators import node
from metafunctions import util

class TestIntegration(BaseTestCase):
    def test_store(self):
        abc = a | b | util.store('output') | c

        self.assertEqual(abc('_'), '_abc')
        self.assertEqual(abc.data['output'], '_ab')

    def test_recall(self):
        a.data['k'] = 'secret'

        cmp = a + b | util.store('k') | c + util.recall('k')
        self.assertEqual(cmp('_'), '_a_bc_a_b')

        cmp = a + b | util.store('k') | c + util.recall('k') | util.recall('k', from_meta=a)
        self.assertEqual(cmp('_'), 'secret')

@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
