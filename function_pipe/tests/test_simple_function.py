import operator

from function_pipe.meta_function import SimpleFunction
from function_pipe.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_decorator(self):
        self.assertEqual(a.__name__, 'a')
        self.assertEqual(a.__module__, __name__)


@SimpleFunction
def a(x):
    return x + 'a'
@SimpleFunction
def b(x):
    return x + 'b'
l = SimpleFunction(lambda x: x + 'l')
