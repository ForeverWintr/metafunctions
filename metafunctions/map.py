import typing as tp
import itertools

from metafunctions.concurrent import FunctionMerge
from metafunctions.operators import concat


class MergeMap(FunctionMerge):
    def __init__(self, function:tp.Callable, merge_function:tp.Callable=concat):
        super().__init__(merge_function, (function, ))

    def _get_call_iterators(self, args):
        '''
        Each element in args is an iterable.
        '''
        args_iter = zip(*args)

        # Note that EVERY element in the func iter will be called, so we need to make sure the
        # length of our iterator is the same as the shortest iterable we received.
        shortest_arg = min(args, key=len)
        func_iter = itertools.repeat(self.functions[0], len(shortest_arg))
        return args_iter, func_iter

    def _call_function(self, f, args:tuple, kwargs:dict):
        '''In MergeMap, args will be a single element tuple containing the args for this function.
        '''
        return f(*args[0], **kwargs)
