import colors

from collections import namedtuple, defaultdict, OrderedDict
from metafunctions.util import system_supports_color


class CallState:
    Node = namedtuple('Node', 'function insert_index')
    def __init__(self):
        '''
        A call tree keeps track of function execution order in metafunctions. This is used to
        accurately determine the location of the currently active function, and to identify
        exception locations. It can be thought of as a metafunction aware call stack.
        '''
        # Meta entry is conceptually the root node of the call tree
        self._meta_entry = None
        self.active_node = None
        self._nodes_visited = 0

        # A dictionary of {child: parent} functions
        self._bottom_up = OrderedDict()

        # A dictionary of {parent: [children]}, in call order
        self._horizontal = defaultdict(list)
        self.data = {}

    def push(self, f):
        '''
        Push a function onto the tree
        '''
        if self._meta_entry is None:
            node = self.Node(f, self._nodes_visited)
            self._meta_entry = node
        else:
            node = self.Node(f, self._nodes_visited)
            self._bottom_up[node] = self.active_node
            self._horizontal[self.active_node].append(node)
        self._nodes_visited += 1
        self.active_node = node

    def pop(self):
        '''Remove last inserted f from the call tree.'''
        try:
            node, parent = self._bottom_up.popitem()
        except KeyError:
            m = self._meta_entry
            self._meta_entry = None
            self.active_node = None
            return m
        self._horizontal.pop(node, None)
        self.active_node = parent
        return node[0]

    def highlight_active_function(self, color=colors.red, use_color=system_supports_color()):
        '''
        Return a formatted string showing the location of the most recently called function in
        call_state.

        Consider this a 'you are here' when called from within a function pipeline.
        '''
        asdf
