from metafunctions.core import SimpleFunction
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_decorator(self):
        self.assertEqual(a.__name__, 'a')
        self.assertEqual(a.__module__, __name__)

    def test_call(self):
        self.assertEqual(a('_'), '_a')
        self.assertEqual(l('_'), '_l')

    def test_str(self):
        self.assertEqual(repr(a), 'SimpleFunction({0!r})'.format(a._function))
        self.assertEqual(str(a), 'a')


@SimpleFunction
def a(x):
    return x + 'a'
l = SimpleFunction(lambda x: x + 'l')
