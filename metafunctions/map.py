import typing as tp

from metafunctions.concurrent import FunctionMerge
from metafunctions.operators import concat


class MergeMap(FunctionMerge):
    def __init__(self, function:tp.Callable, merge_function:tp.Callable=concat):
        super().__init__(merge_function, (function, ))

