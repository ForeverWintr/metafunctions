
import unittest

from metafunctions.tests.util import BaseTestCase
from metafunctions.decorators import node
from metafunctions import util

class TestIntegration(BaseTestCase):
    def test_store(self):

        self.fail()

@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
