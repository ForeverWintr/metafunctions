"""
Extra operators used by MetaFunctions
"""
from operator import add, sub, truediv, mul


def concat(*args):
    "concat(1, 2, 3) -> (1, 2, 3)"
    return args
