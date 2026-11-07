import os
from unittest import mock

from metafunctions import util
from metafunctions.api import locate_error, node
from metafunctions.tests.simple_nodes import *
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_locate_error(self):
        @node
        def fail(x):
            raise ZeroDivisionError("division by zero")

        cmp = a + b | (c & fail & fail)
        with_tb = locate_error(cmp, use_color=False)

        with self.assertRaises(ZeroDivisionError) as e:
            cmp("x")
        self.assertEqual(str(e.exception), "division by zero")

        with self.assertRaises(ZeroDivisionError) as e:
            with_tb("x")
        self.assertEqual(
            str(e.exception),
            "division by zero \n\nOccured in the following function: ((a + b) | (c & ->fail<- & fail))",
        )

        # regular calls still work
        with_tb2 = locate_error(a | b | c)
        self.assertEqual(with_tb2("_"), "_abc")

        self.assertEqual(str(with_tb), str(cmp))
        self.assertEqual(str(with_tb), "((a + b) | (c & fail & fail))")
        self.assertEqual(str(with_tb2), "(a | b | c)")

    def test_replace_nth(self):
        s = "aaaaaaaaaa"
        self.assertEqual(util.replace_nth(s, "aa", 3, "BB"), "aaaaBBaaaa")

        new = util.replace_nth(s, "nothere", 1, "BB")
        self.assertEqual(new, s)

    def test_color_highlights(self):
        s = "a ->test<- string ->for<- highlight"
        self.assertEqual(
            util.color_highlights(s),
            "a {} string {} highlight".format(
                util.red("->test<-"), util.red("->for<-")
            ),
        )

    def test_red(self):
        self.assertEqual(util.red("x"), "\x1b[31mx\x1b[0m")

    def test_system_supports_color(self):
        tty = mock.Mock(isatty=lambda: True)
        not_tty = mock.Mock(isatty=lambda: False)

        def supports_color(env, platform="linux", stdout=tty):
            with (
                mock.patch.dict(os.environ, env, clear=True),
                mock.patch.object(util.sys, "platform", platform),
                mock.patch.object(util.sys, "stdout", stdout),
            ):
                return util.system_supports_color()

        # Default: color only on a tty, and never on windows
        self.assertTrue(supports_color({}))
        self.assertFalse(supports_color({}, stdout=not_tty))
        self.assertFalse(supports_color({}, stdout=object()))
        self.assertFalse(supports_color({}, platform="win32"))

        # NO_COLOR disables color
        self.assertFalse(supports_color({"NO_COLOR": "1"}))
        self.assertTrue(supports_color({"NO_COLOR": ""}))

        # FORCE_COLOR enables color, even without a tty or on windows
        self.assertTrue(supports_color({"FORCE_COLOR": "1"}, stdout=not_tty))
        self.assertTrue(supports_color({"FORCE_COLOR": "1"}, platform="win32"))
        self.assertFalse(supports_color({"FORCE_COLOR": ""}, stdout=not_tty))

        # NO_COLOR takes precedence over FORCE_COLOR
        self.assertFalse(supports_color({"NO_COLOR": "1", "FORCE_COLOR": "1"}))
