from collections import namedtuple, defaultdict, OrderedDict

class CallState:
    __slots__ = (
        'data',
        '_meta_stack',
        '_exception',
        '_exception_meta_stack',
    )
    def __init__(self):
        '''An object for holding state during a metafunction call.'''
        self.data = {}
        self._meta_stack = []
        self._exception = None
        self._exception_meta_stack = None

    def set_exception(self, exception):
        '''
        Called to indicate that an exception has occured on this call_state. Saves the exception,
        as well as freezes a copy of the meta_stack where the exception occured.
        '''
        if exception is not self._exception:
            self._exception = exception
            self._exception_meta_stack = tuple(self._meta_stack)


class CallTree:
    Node = namedtuple('Node', 'function insert_index')
    def __init__(self):
        '''
        A call tree keeps track of function execution order in metafunctions. This is used to
        accurately determine the location of the currently active function, and to identify
        exception locations. It can be thought of as a metafunction aware call stack.
        '''
        # Meta entry is conceptually the root node of the call tree
        self._meta_entry = None
        self._active_node = None
        self._nodes_visited = 0

        # A dictionary of {child: parent} functions
        self._bottom_up = OrderedDict()

        # A dictionary of {parent: [children]}, in call order
        self._horizontal = defaultdict(list)

    def push(self, f):
        '''
        Push a function onto the tree
        '''
        if self._meta_entry is None:
            node = self.Node(f, self._nodes_visited)
            self._meta_entry = node
        else:
            node = self.Node(f, self._nodes_visited)
            self._bottom_up[node] = self._active_node
            self._horizontal[self._active_node].append(node)
        self._nodes_visited += 1
        self._active_node = node

    def pop(self):
        '''Remove last inserted f from the call tree.'''
        try:
            node, parent = self._bottom_up.popitem()
        except KeyError:
            m = self._meta_entry
            self._meta_entry = None
            self._active_node = None
            return m
        self._horizontal.pop(node, None)
        self._active_node = parent
        return node[0]


