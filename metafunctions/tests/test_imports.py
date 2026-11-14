import importlib
import importlib.metadata
import random
import unittest
from unittest import mock

import metafunctions


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
            exec(f"from metafunctions import {name}")  # noqa: S102

    def test_version_not_installed(self):
        # Reload again afterwards so later tests see the real version
        self.addCleanup(importlib.reload, metafunctions)
        with mock.patch(
            "importlib.metadata.version",
            side_effect=importlib.metadata.PackageNotFoundError("metafunctions"),
        ):
            importlib.reload(metafunctions)
        self.assertEqual(metafunctions.__version__, "unknown")
