import unittest
import random


class TestUnit(unittest.TestCase):
    def test_api_imports(self):
        expected_names = [
            "node",
            "bind_call_state",
            "star",
            "store",
            "recall",
            "concurrent",
            "mmap",
            "locate_error",
        ]
        random.shuffle(expected_names)
        for name in expected_names:
            exec("from metafunctions import {}".format(name))
