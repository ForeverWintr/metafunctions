
from metafunctions.util import node, store, recall

@node
def a(x):
    return x + 'a'
@node
def b(x):
    return x + 'b'
@node
def c(x):
    return x + 'c'


f = a | b | c
print('f = {}'.format(f))
input()


g = a + b | store('AB') | (c * 2) + recall('AB')
print('g = {}'.format(g))
input()


h = f & g
print('h = {}'.format(h))
