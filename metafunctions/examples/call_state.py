
from metafunctions.util import node, bind_call_state

from string_processing import a, cat


#@fpn.pipe_node_factory
#def replace_init(chars, **kwargs):
    #return kwargs[fpn.PREDECESSOR_RETURN].replace(kwargs[fpn.PN_INPUT], chars)

def replace_init(chars):
    @node
    @bind_call_state
    def replacer(call_state, s):
        return s.replace(call_state.call_args[0], chars)
    return replacer


#f = init | a | cat('b') | cat('c') * 2 | replace_init('+')
f = a | cat('b') | cat('c') * 2 | replace_init('+')

#assert f['*'] == '+abc+abc'
assert f('*') == '+abc+abc'


