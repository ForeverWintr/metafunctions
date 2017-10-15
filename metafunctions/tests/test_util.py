from unittest import mock
import functools

import colors

from metafunctions.tests.util import BaseTestCase
from metafunctions.tests.simple_nodes import *
from metafunctions.api import store, recall, node, bind_call_state, locate_error, mmap
from metafunctions import util
from metafunctions.core import SimpleFunction, CallState


class TestUnit(BaseTestCase):
    def test_locate_error(self):

        @node
        def fail(x):
            1 / 0

        cmp = a + b | (c & fail & fail)
        with_tb = locate_error(cmp)

        with self.assertRaises(ZeroDivisionError) as e:
            cmp('x')
        self.assertEqual(str(e.exception), 'division by zero')

        with self.assertRaises(ZeroDivisionError) as e:
            with_tb('x')
        self.assertEqual(str(e.exception),
                'division by zero \n\nOccured in the following function: ((a + b) | (c & ->fail<- & fail))')

        # regular calls still work
        with_tb2 = locate_error(a|b|c)
        self.assertEqual(with_tb2('_'), '_abc')

        self.assertEqual(str(with_tb), str(cmp))
        self.assertEqual(str(with_tb), '((a + b) | (c & fail & fail))')
        self.assertEqual(str(with_tb2), '(a | b | c)')

    def test_replace_nth(self):
        s = 'aaaaaaaaaa'
        self.assertEqual(util.replace_nth(s, 'aa', 3, 'BB'), 'aaaaBBaaaa')

        new = util.replace_nth(s, 'nothere', 1, 'BB')
        self.assertEqual(new, s)

    def test_color_highlights(self):
        s = 'a ->test<- string ->for<- highlight'
        self.assertEqual(util.color_highlights(s), f'a {colors.red("->test<-")} string {colors.red("->for<-")} highlight')
