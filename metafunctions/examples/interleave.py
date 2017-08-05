
from metafunctions.util import node, bind_call_state, store, recall

from string_processing import a, cat
from call_state import replace_init


#@fpn.pipe_node_factory
#def interleave(chars, **kwargs):
    #pred = kwargs[fpn.PREDECESSOR_RETURN]
    #post = []
    #for i, c in enumerate(pred):
        #post.append(c)
        #post.append(chars[i % len(chars)])
    #return ''.join(post)

@node
def interleave(pred, chars):
    post = []
    for i, c in enumerate(pred):
        post.append(c)
        post.append(chars[i % len(chars)])
    return ''.join(post)




#h = init | cat('@@') | cat('__') * 2
h = cat('@@') | cat('__') * 2

#f = init | a | cat('b') | cat('c') * 3 | replace_init('+') | interleave(h)
f = store('input') | a | cat('b') | cat('c') * 3 | (replace_init('+') & (recall('input') | h)) @ interleave

#assert f['*'] == '+*a@b@c_+_a*b@c@+_a_b*c@'
assert f('*') == '+*a@b@c_+_a*b@c@+_a_b*c@'

# Or perhaps more clearly
g =  a | cat('b') | cat('c') * 3 | replace_init('+')
f2 =  (g & h) | interleave

assert f2('*') == '+*a@b@c_+_a*b@c@+_a_b*c@'
