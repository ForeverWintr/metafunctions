import random

from metafunctions.util import node



@node
def a(x):
    1 / random.choice((0, 1, 2, 3, 4))
    return x + 'a'

@node
def b(x):
    1 / random.choice((0, 1, 2, 3, 4))
    return x + 'b'

@node
def c(x):
    1 / random.choice((0, 1, 2, 3, 4))
    return x + 'c'


f = a | b | c | (c + c + c) | b * 10 | (a & a & a & a)

print(f('x'))
