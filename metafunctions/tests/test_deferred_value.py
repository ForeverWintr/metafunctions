from metafunctions.core import DeferredValue
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_call(self):
        self.assertEqual(DeferredValue(5)(), 5)
        a = object()
        b = DeferredValue(a)
        self.assertIs(b(), a)

    def test_str_repr(self):
        a = object()
        b = DeferredValue(a)
        self.assertEqual(repr(b), f'DeferredValue({repr(a)})')
        self.assertEqual(str(DeferredValue(5)), '5')
        self.assertEqual(repr(DeferredValue('a')), "DeferredValue('a')")
