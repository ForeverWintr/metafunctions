'''
Some simple nodes to use in tests.
'''
from metafunctions.api import node


@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
@node
def d(x):
    return x + 'd'
@node
def e(x):
    return x + 'e'
