
from metafunctions.tests.util import BaseTestCase
from metafunctions.tests.simple_nodes import *
from metafunctions.api import bind_call_state
from metafunctions.api import node
from metafunctions.api import mmap
from metafunctions.api import locate_error
from metafunctions.core import CallState


class TestUnit(BaseTestCase):
    def test_bind_call_state(self):
        # Bound functions receive call state
        @node
        @bind_call_state
        def f(call_state, x):
            self.assertIsInstance(call_state, CallState)
            call_state.data['h'] = 'b'
            return x + 'f'

        @node
        def g(x):
            return x + 'g'

        @node
        @bind_call_state
        def h(call_state, x):
            self.assertIsInstance(call_state, CallState)
            return x + call_state.data['h']

        fg = f | g | h
        self.assertEqual(fg('_'), '_fgb')

    def test_provide_call_state(self):
        # A call state you provide is passed to all functions
        @node
        @bind_call_state
        def f(call_state, x):
            self.assertIs(call_state, c)
            call_state.data['h'] = 'd'
            return x + 'f'
        @node
        def g(x):
            return x + 'g'
        @node
        @bind_call_state
        def h(call_state, x):
            self.assertIs(call_state, c)
            return x + call_state.data['h']
        fg = f | g | h

        c = CallState()
        self.assertEqual(fg('_', call_state=c), '_fgd')

    def test_add_remove(self):
        # imagine these are functions
        a, b, c, d = 'a b c d'.split()
        Node = CallState.Node

        tree = CallState()
        tree.push(a)
        tree.push(a)
        self.assertEqual(tree.pop(), a)
        self.assertDictEqual(tree._parents, {})

        tree.push(b)
        tree.push(a)
        self.assertDictEqual(tree._parents,
                             {Node(b, 2): Node(a, 0),
                              Node(a, 3): Node(b, 2)})
        self.assertDictEqual(tree._children,
                             {Node(a, 0): [Node(a, 1), Node(b, 2)],
                              Node(b, 2): [Node(a, 3)],})

        tree.push(b)
        self.assertDictEqual(tree._children,
                             {Node(a, 0): [Node(a, 1), Node(b, 2)],
                              Node(b, 2): [Node(a, 3)],
                              Node(a, 3): [Node(b, 4)],})
        self.assertDictEqual(tree._parents,
                             {Node(b, 4): Node(a, 3),
                              Node(a, 3): Node(b, 2),
                              Node(b, 2): Node(a, 0),})

        self.assertEqual(tree.pop(), b)
        self.assertEqual(tree.pop(), a)
        for f in a, b, c, d:
            tree.push(f)
            tree.pop()
        self.assertDictEqual(tree._children,
                {Node(a, 0): [Node(a, 1), Node(b, 2)],
                 Node(b, 2): [Node(a, 3), Node(a, 5), Node(b, 6), Node(c, 7), Node(d, 8)]})
        self.assertDictEqual(tree._parents, {Node(b, 2): Node(a, 0),})

    def test_iter_parent_nodes(self):
        @node
        def l(*args):
            return []
        @node
        @bind_call_state
        def return_parent_nodes(cs, *args):
            return list(cs.iter_parent_nodes(cs.active_node))

        def nodes2str(nodes):
            return [(str(p.function), p.insert_index) for p in nodes]
        def get_parents(f):
            cs = CallState()
            return nodes2str(f('', call_state=cs))

        self.assertEqual(return_parent_nodes(), [(return_parent_nodes, 0)])

        #create some crazy compositions to get parents out of
        simple_chain = a | b | c | return_parent_nodes
        self.assertListEqual(get_parents(simple_chain), [(str(simple_chain), 0)])

        merges = l + (l + (l + return_parent_nodes))
        self.assertListEqual(get_parents(merges), [
            ('(l + return_parent_nodes)', 4),
            ('(l + (l + return_parent_nodes))', 2),
            ('(l + (l + (l + return_parent_nodes)))', 0)])

    def test_highlight_active_function(self):
        fmt_index = 7

        @node
        def ff(x):
            return x + 'F'

        @node
        @bind_call_state
        def f(call_state, x):
            if call_state._nodes_visited == fmt_index:
                location_string = call_state.highlight_active_function()
                self.assertEqual(location_string, '(a | b | ff | f | f | ->f<- | f | f)')
                self.assertEqual(x, '_abFff')
            return x + 'f'

        pipe = a | b | ff | f | f | f | f | f
        pipe('_')

        state = CallState()
        af = a + f
        af('_', call_state=state)
        with self.assertRaises(AttributeError):
            curr_f = state.highlight_active_function()

    def test_hightlight_active_function_no_parents(self):
        @node
        @bind_call_state
        def f(cs):
            return cs.highlight_active_function()

        self.assertEqual(f(), '->f<-')

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
        mapper = locate_error(('aaaaa', 'BBBBB') | mmap(cmp), use_color=False)
        with self.assertRaises(ZeroDivisionError) as e:
            mapper()
        self.assertEqual(str(e.exception),
                "division by zero \n\nOccured in the following function: "
                "(('aaaaa', 'BBBBB') | mmap(((a + b) | (c & no_fail & ->fail<-))))")
