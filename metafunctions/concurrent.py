import multiprocessing

from metafunctions.core import FunctionMerge


class ConcurrentMerge(FunctionMerge):
    def __init__(self, function_merge: FunctionMerge):
        '''A subclass of FunctionMerge that calls each of its component functions in parallel.

        ConcurrentMerge takes a FunctionMerge object and upgrades it.
        '''
        self._merge_func = function_merge._merge_func
        self._functions = function_merge._functions
        self._format = function_merge._format

    def __call__(self, *args, **kwargs):
        pool = multiprocessing.Pool(processes=2)
