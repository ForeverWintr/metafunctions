
from metafunctions.core import FunctionMerge
from metafunctions.core import inject_call_state


class BroadcastMerge(FunctionMerge):
    def __init__(self, function_merge: FunctionMerge):
        '''A subclass of FunctionMerge that receives an iterable and calls each of its component
        functions with one element of the iterable.

        BroadcastMerge takes a FunctionMerge object and upgrades it.
        '''
        super().__init__(
                function_merge._merge_func,
                function_merge._functions,
                function_merge._function_join_str)

    def __str__(self):
        joined_funcs = super().__str__()
        return f"star{joined_funcs}"

    @inject_call_state
    def __call__(self, *args, **kwargs):
        pass
