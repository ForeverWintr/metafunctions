import operator
from unittest import mock
import functools

import colors

from metafunctions.tests.util import BaseTestCase
from metafunctions.util import node
from metafunctions.util import bind_call_state
from metafunctions.util import highlight_current_function
from metafunctions.util import concurrent
from metafunctions.util import mmap
from metafunctions.util import store
from metafunctions.util import star
from metafunctions.concurrent import ConcurrentMerge
from metafunctions import operators
from metafunctions.core import CallState
from metafunctions.exceptions import ConcurrentException, CompositionError, CallError


class TestIntegration(BaseTestCase):
    def test_basic(self):
        ab = a + b
        cab = ConcurrentMerge(ab)
        self.assertEqual(cab('_'), '_a_b')

    @mock.patch('metafunctions.util.highlight_current_function')
    def test_exceptions(self, mock_h):
        mock_h.side_effect = functools.partial(highlight_current_function, use_color=True)
        @node
        def fail(x):
            if not x:
                1 / 0
            return x - 1

        cmp = ConcurrentMerge(fail - fail)

        with self.assertRaises(ConcurrentException) as e:
            cmp(0)
        self.assertIsInstance(e.exception.__cause__, ZeroDivisionError)
        self.assertEqual(e.exception.__cause__.args[0],
                f'division by zero \n\nOccured in the following function: '
                f'concurrent({colors.red("->fail<-")} - fail)')

    def test_consistent_meta(self):
        '''
        Every function in the pipeline recieves the same meta.
        '''
        @node
        @bind_call_state
        def f(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1
        @node()
        @bind_call_state
        def g(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1
        @node
        @bind_call_state
        def h(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1
        @node
        @bind_call_state
        def i(call_state, x):
            self.assertIs(call_state._meta_entry, cmp)
            return 1

        cmp = ConcurrentMerge(h + f + f / h + i - g)
        self.assertEqual(cmp(1), 3)

        self.assertEqual(cmp(1, call_state=cmp.new_call_state()), 3)

        # how do pretty tracebacks work in multiprocessing?

    def test_call(self):
        c = concurrent(a+b)
        self.assertEqual(c('_'), '_a_b')
        self.assertEqual(c('-', '_'), '-a_b')
        with self.assertRaises(CallError):
            c('_', '_', '_')

        @node
        def d():
            return 'd'
        abd = concurrent(a & b & d)
        self.assertEqual(abd('-', '_'), ('-a', '_b', 'd'))

    def test_concurrent(self):
        c = concurrent(a + b)
        self.assertIsInstance(c, ConcurrentMerge)
        self.assertEqual(c('_'), '_a_b')

    def test_not_concurrent(self):
        #can only upgrade FunctionMerges

        with self.assertRaises(CompositionError):
            concurrent(a)
        with self.assertRaises(CompositionError):
            concurrent(a | b)

    def test_str_repr(self):
        cab = ConcurrentMerge(a + b)
        cmap = concurrent(mmap(a))

        self.assertEqual(repr(cab), f'ConcurrentMerge({operator.add}, ({repr(a)}, {repr(b)}))')
        self.assertEqual(str(cab), f'concurrent(a + b)')
        self.assertEqual(str(cmap), f'concurrent(mmap(a))')

    def test_basic_map(self):
        # We can upgrade maps to run in parallel
        banana = 'bnn' | concurrent(mmap(a)) | ''.join
        str_concat = operators.concat | node(''.join)
        batman = concurrent(mmap(a, operator=str_concat))
        self.assertEqual(banana(), 'banana')
        self.assertEqual(batman('nnnn'), 'nananana')

    def test_multi_arg_map(self):
        @node
        def f(*args):
            return args

        m = concurrent(mmap(f))

        with self.assertRaises(CompositionError):
            #Because star returns a simple function, we can't upgrade it.
            starmap = concurrent(star(mmap(f)))
        #we have to wrap concurrent in star instead.
        starmap = star(concurrent(mmap(f)))

        mapstar = concurrent(mmap(star(f)))

        self.assertEqual(m([1, 2, 3], [4, 5, 6]), ((1, 4), (2, 5), (3, 6)))
        self.assertEqual(m([1, 2, 3]), ((1, ), (2, ), (3, )))

        with self.assertRaises(TypeError):
            starmap([1, 2, 3])
        self.assertEqual(starmap([[1, 2, 3]]), m([1, 2, 3]))

        cmp = ([1, 2, 3], [4, 5, 6]) | starmap
        self.assertEqual(cmp(), ((1, 4), (2, 5), (3, 6)))

        cmp = ([1, 2, 3], [4, 5, 6]) | mapstar
        self.assertEqual(cmp(), ((1, 2, 3), (4, 5, 6)))

    def test_call_state(self):
        # Call state should be usable in concurrent chains
        chain_a = a | b | store('ab')
        chain_b = b | a | store('ba')
        cmp = concurrent(chain_a & chain_b)
        state = CallState()

        self.assertEqual(cmp('_', call_state=state), ('_ab', '_ba'))
        self.assertDictEqual(state.data, {'ab': '_ab', 'ba': '_ba'})

        # If call_state.data contains something that isn't pickleable, fail gracefully
        bad = [lambda: None] | store('o')
        cmp = concurrent(bad & bad)
        with self.assertRaises(ConcurrentException):
            cmp()

    def test_unpicklable_return(self):
        # Concurrent can't handle functions that return unpicklable objects. Raise a descriptive
        # exception
        @node
        def f():
            return lambda:None
        cmp = concurrent(f & f)
        with self.assertRaises(ConcurrentException):
            cmp()

    def test_unpicklable_exception(self):
        # Don't let child processes crash, even if they do weird things like raise unpickleable
        # exceptions
        @node
        def f():
            class BadException(Exception):
                pass
            raise BadException()

        cmp = concurrent(f+f)
        with self.assertRaises(ConcurrentException):
            cmp()

    @mock.patch('metafunctions.concurrent.os.fork', return_value=0)
    @mock.patch('metafunctions.concurrent.os._exit')
    @mock.patch('multiprocessing.queues.Queue.close')
    @mock.patch('multiprocessing.queues.Queue.join_thread')
    @mock.patch('metafunctions.concurrent.os.waitpid')
    def test_no_fork(self, mock_wait, mock_join, mock_close, mock_exit, mock_fork):
        # This test re-runs concurrent tests with forking disabled. Partially this is to
        # address my inability to get coverage.py to recognize the code covered by forked
        # processes, but it's also useful to have single process coverage of _process_in_fork to
        # detect errors that may be squelched by the interactions of multiple processes

        # Re-run all tests with fork patched
        this_test = self.id().split('.')[-1]
        for test_name in (t for t in dir(self) if t.startswith('test_') and t != this_test):
            method = getattr(self, test_name)
            print('calling, ', method)
            with self.subTest(name=test_name):
                method()


### Simple Sample Functions ###
@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
