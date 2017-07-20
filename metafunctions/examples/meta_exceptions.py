import random

from metafunctions.util import node


@node
def often_numeric(x=None):
    return random.choice(('1', '2', '3', 'potato'))


to_float = often_numeric | float

f = to_float + to_float + to_float * to_float

print(f())
