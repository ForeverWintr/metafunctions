
from metafunctions.util import node, store, recall


average = node(sum) / len

@node
def say_hello(name):
    return 'Hello {}!'.format(name)


greet = input | say_hello | print

big_greet = input | store('name') | say_hello + (2*recall('name')) | print
