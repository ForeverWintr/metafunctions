from metafunctions.tests.util import BaseTestCase
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
        self.assertDictEqual(tree._bottom_up, {})

        tree.push(b)
        tree.push(a)
        self.assertDictEqual(tree._bottom_up,
                             {Node(b, 2): Node(a, 0),
                              Node(a, 3): Node(b, 2)})
        self.assertDictEqual(tree._horizontal,
                             {Node(a, 0): [Node(a, 1), Node(b, 2)],
                              Node(b, 2): [Node(a, 3)],})

        tree.push(b)
        self.assertDictEqual(tree._horizontal,
                             {Node(a, 0): [Node(a, 1), Node(b, 2)],
                              Node(b, 2): [Node(a, 3)],
                              Node(a, 3): [Node(b, 4)],})
        self.assertDictEqual(tree._bottom_up,
                             {Node(b, 4): Node(a, 3),
                              Node(a, 3): Node(b, 2),
                              Node(b, 2): Node(a, 0),})

        self.assertEqual(tree.pop(), b)
        self.assertEqual(tree.pop(), a)
        for f in a, b, c, d:
            tree.push(f)
            tree.pop()
        self.assertDictEqual(tree._horizontal,
                {Node(a, 0): [Node(a, 1), Node(b, 2)],
                 Node(b, 2): [Node(a, 3), Node(a, 5), Node(b, 6), Node(c, 7), Node(d, 8)]})
        self.assertDictEqual(tree._bottom_up, {Node(b, 2): Node(a, 0),})

