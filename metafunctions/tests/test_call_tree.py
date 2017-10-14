from metafunctions.tests.util import BaseTestCase
from metafunctions.tests.simple_nodes import *
from metafunctions.api import bind_call_state
from metafunctions.api import node
from metafunctions.core._call_state import CallState, CallState


class TestUnit(BaseTestCase):
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
        def return_active_node(cs, *args):
            return list(cs.iter_parent_nodes(cs.active_node))

        def nodes2str(nodes):
            return [(str(p.function), p.insert_index) for p in nodes]
        def get_parents(f):
            cs = CallState()
            return nodes2str(f('', call_state=cs))

        #create some crazy compositions to get parents out of
        simple_chain = a | b | c | return_active_node
        self.assertListEqual(get_parents(simple_chain), [(str(simple_chain), 0)])

        merges = l + (l + (l + return_active_node))
        self.assertListEqual(get_parents(merges), [
            ('(l + return_active_node)', 4),
            ('(l + (l + return_active_node))', 2),
            ('(l + (l + (l + return_active_node)))', 0)])

