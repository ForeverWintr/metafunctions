from unittest import mock
import functools

import colors

from metafunctions.tests.util import BaseTestCase
from metafunctions.tests.simple_nodes import *
from metafunctions.api import store, recall, node, bind_call_state, locate_error, mmap
from metafunctions import util
from metafunctions.core import SimpleFunction, CallState


class TestUnit(BaseTestCase):
    def test_highlight_active_function(self):
        fmt_index = 7

        @node
        def ff(x):
            return x + 'F'

        @node
        @bind_call_state
        def f(call_state, x):
            if call_state._nodes_visited == fmt_index:
                location_string = call_state.highlight_active_function(use_color=False)
                location_string_color = call_state.highlight_active_function(use_color=True)
                self.assertEqual(location_string, '(a | b | ff | f | f | ->f<- | f | f)')
                self.assertEqual(location_string_color,
                        '(a | b | ff | f | f | \x1b[31m->f<-\x1b[0m | f | f)')
                self.assertEqual(x, '_abFff')
            return x + 'f'

        pipe = a | b | ff | f | f | f | f | f
        pipe('_')

        state = CallState()
        af = a + f
        af('_', call_state=state)
        with self.assertRaises(AttributeError):
            curr_f = state.highlight_active_function(use_color=False)

    def test_highlight_active_function_multichar(self):
        # Don't fail on long named functions. This is a regression test
        @node
        def fail(x):
            if not x:
                1 / 0
            return x - 1

        cmp = fail | fail + a
        color = locate_error(cmp, use_color=True)
        no_color = locate_error(cmp, use_color=False)
        with self.assertRaises(ZeroDivisionError) as e:
            color(1)
        self.assertTrue(e.exception.args[0].endswith('(fail | (\x1b[31m->fail<-\x1b[0m + a))'))
        with self.assertRaises(ZeroDivisionError) as e:
            no_color(1)
        self.assertTrue(e.exception.args[0].endswith('(fail | (->fail<- + a))'))

    def test_highlight_with_map(self):
        @node
        def no_fail(x):
            return x
        @node
        def fail(*args):
            1 / 0

        cmp = a + b | (c & no_fail & fail)
        mapper = locate_error(('aaaaa', 'BBBBB') | mmap(cmp))
        with self.assertRaises(ZeroDivisionError) as e:
            mapper()
        self.assertEqual(str(e.exception),
                "division by zero \n\nOccured in the following function: "
                "(('aaaaa', 'BBBBB') | mmap(((a + b) | (c & no_fail & ->fail<-))))")

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
