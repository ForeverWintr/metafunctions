"""
Extra operators used by MetaFunctions
"""

# These are imported for use elsewhere
from operator import add  # noqa: F401
from operator import mul  # noqa: F401
from operator import sub  # noqa: F401
from operator import truediv  # noqa: F401


def concat(*args):
    "concat(1, 2, 3) -> (1, 2, 3)"
    return args
