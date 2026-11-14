from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from metafunctions.api import bind_call_state
from metafunctions.api import concurrent
from metafunctions.api import locate_error
from metafunctions.api import mmap
from metafunctions.api import node
from metafunctions.api import recall
from metafunctions.api import star
from metafunctions.api import store

try:
    __version__ = version("metafunctions")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "bind_call_state",
    "concurrent",
    "locate_error",
    "mmap",
    "node",
    "recall",
    "star",
    "store",
]
