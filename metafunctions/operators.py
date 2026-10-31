"""
Extra operators used by MetaFunctions
"""

# These are imported for use elsewhere
from operator import add, mul, sub, truediv  # noqa: F401


def concat(*args):
    "concat(1, 2, 3) -> (1, 2, 3)"
    return args
