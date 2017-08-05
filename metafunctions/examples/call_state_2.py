
from metafunctions.util import node, bind_call_state, store, recall

from string_processing import a
from call_state import replace_init
from interleave import interleave

def cat(chars=''):
    @node
    def inner_cat(s, extra=''):
        return s + chars + extra
    return inner_cat


#class Input(fpn.PipeNodeInput):
    #def __init__(self, chars):
        #super().__init__()
        #self.chars = chars
from metafunctions.core import CallState


#@fpn.pipe_node
#def input_init(**kwargs):
    #return kwargs[fpn.PN_INPUT].chars


#p = input_init | cat('www') | fpn.store('p')
p = cat('www') | store('p')


#q = input_init | cat('@@') | cat('__') * 2 | fpn.store('q')
q = cat('@@') | cat('__') * 2 | store('q')


#r = (input_init | a | cat(fpn.recall('p')) | cat('c') * 3
        #| interleave(fpn.recall('q')))
r = (((a & recall('p')) @ cat() | cat('c') * 3) & recall('q')) @ interleave


#f = fpn.call(p, q, r)
#pni = Input('x')
#assert f[pni] == 'xxa@x@w_w_wxc@x@a_x_wxw@w@c_x_axx@w@w_w_cx'
call_state = CallState()
p('x', call_state=call_state)
q('x', call_state=call_state)
assert r('x', call_state=call_state) == 'xxa@x@w_w_wxc@x@a_x_wxw@w@c_x_axx@w@w_w_cx'



#f = fpn.call(p, q, r)
from operator import itemgetter
f = (p & q & r) | itemgetter(-1)


#assert f[pni] == 'xxa@x@w_w_wxc@x@a_x_wxw@w@c_x_axx@w@w_w_cx'
assert f('x') == 'xxa@x@w_w_wxc@x@a_x_wxw@w@c_x_axx@w@w_w_cx'
