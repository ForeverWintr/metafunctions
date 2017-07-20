
from metafunctions.util import node


#a = fpn.pipe_node(lambda **kwargs: kwargs[fpn.PREDECESSOR_RETURN] + 'a')

a = node(lambda s: s + 'a')


#@fpn.pipe_node
#@fpn.pipe_kwarg_bind(fpn.PREDECESSOR_RETURN)
#def a(s):
    #return s + 'a'

@node
def a(s):
    return s + 'a'


#@fpn.pipe_node_factory
#def cat(chars, **kwargs):
    #return kwargs[fpn.PREDECESSOR_RETURN] + chars

def cat(chars):
    @node
    def inner_cat(s):
        return s + chars
    return inner_cat


# f = init | a | cat('b') | cat('c')
f = a | cat('b') | cat('c')

#assert f(**{fpn.PN_INPUT: '*'}) == '*abc'
#assert f(**{fpn.PN_INPUT: '+'}) == '+abc'
#assert f['*'] == '*abc'
assert f('*') == '*abc'
assert f('+') == '+abc'

