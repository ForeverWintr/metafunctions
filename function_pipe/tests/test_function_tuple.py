import operator

from function_pipe.meta_function import FunctionTuple
from function_pipe.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_str(self):
        def f1():
            pass
        def f2():
            pass
        ft = FunctionTuple(operator.add, f1, f2)
        self.assertEqual(str(ft), f'{f1} + {f2}')
