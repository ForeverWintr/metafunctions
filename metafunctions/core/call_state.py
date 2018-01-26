from collections import namedtuple, defaultdict, OrderedDict
from metafunctions import util


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
        self._parents = OrderedDict()

        # A dictionary of {parent: [children]}, in call order
        self._children = defaultdict(list)
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
            self._parents[node] = self.active_node
            self._children[self.active_node].append(node)
        self._nodes_visited += 1
        self.active_node = node

    def pop(self):
        '''Remove last inserted f from the call tree.'''
        try:
            node, parent = self._parents.popitem()
        except KeyError:
            m = self._meta_entry
            self._meta_entry = None
            self.active_node = None
            return m
        self._children.pop(node, None)
        self.active_node = parent
        return node[0]

    def iter_parent_nodes(self, node):
        '''
        Return an iterator over all parents of this node in the tree, ending with the meta_entry
        point.
        '''
        # if node isn't in _parents, it must be the meta entry
        parent = self._parents.get(node, self._meta_entry)
        yield parent
        if parent is not self._meta_entry:
            yield from self.iter_parent_nodes(parent)

    def highlight_active_function(self):
        '''
        Return a formatted string showing the location of the most recently called function in
        call_state.

        Consider this a 'you are here' when called from within a function pipeline.
        '''
        current_function = self.active_node.function
        current_name = str(current_function)
        new_name = util.highlight(current_name)

        # rename active function in parent (if active function isn't in parent, active function
        # becomes parent)
        for parent in self.iter_parent_nodes(self.active_node):
            parent_name = str(parent.function)

            # Note we count occurences of current name in functions we've called so far. We do this
            # because it's possible previous functions contain the name of this function.
            name_count = sum(str(n.function).count(current_name) for n in self._children[parent])

            new_name = util.replace_nth(parent_name, current_name, name_count, new_name)
            current_function = parent.function
            current_name = parent_name

            # if new parent name hasn't changed (meaning it didn't contain the name we're
            # highlighting), highlight the parent name
            if new_name == parent_name:
                new_name = util.highlight(new_name)
        return new_name





