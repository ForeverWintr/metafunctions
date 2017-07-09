import operator
import typing as tp
import abc
import functools


from metafunctions.core._decorators import binary_operation
from metafunctions.core._decorators import inject_call_state
from metafunctions.core._call_state import CallState


class MetaFunction(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        '''A MetaFunction is a function that contains other functions. When executed, it calls the
        functions it contains.
        '''
        self.data = {}
        self._called_functions = []

    @abc.abstractmethod
    def __call__(self, *args, call_state=None, **kwargs):
        '''Call the functions contained in this MetaFunction'''

    @property
    def functions(self):
        return self._functions

    @staticmethod
    def make_meta(function):
        '''Wrap the given function in a metafunction, unless it's already a metafunction'''
        if not isinstance(function, MetaFunction):
            return SimpleFunction(function)
        return function

    @staticmethod
    def defer_value(value):
        '''Wrap the given value in a DeferredValue object, (which returns its value when called).'''
        return DeferredValue(value)

    @staticmethod
    def new_call_state():
        return CallState()

    ### Operator overloads ###
    @binary_operation
    def __or__(self, other):
        return FunctionChain.combine(self, other)

    @binary_operation
    def __ror__(self, other):
        return FunctionChain.combine(other, self)

    @binary_operation
    def __add__(self, other):
        return FunctionMerge(operator.add, (self, other))

    @binary_operation
    def __radd__(self, other):
        return FunctionMerge(operator.add, (other, self))

    @binary_operation
    def __sub__(self, other):
        return FunctionMerge(operator.sub, (self, other))

    @binary_operation
    def __rsub__(self, other):
        return FunctionMerge(operator.sub, (other, self))

    @binary_operation
    def __mul__(self, other):
        return FunctionMerge(operator.mul, (self, other))

    @binary_operation
    def __rmul__(self, other):
        return FunctionMerge(operator.mul, (other, self))

    @binary_operation
    def __truediv__(self, other):
        return FunctionMerge(operator.truediv, (self, other))

    @binary_operation
    def __rtruediv__(self, other):
        return FunctionMerge(operator.truediv, (other, self))


class FunctionChain(MetaFunction):
    def __init__(self, functions:tuple):
        '''A FunctionChain is a metafunction that calls its functions in sequence, passing the
        results of the first function subsequent functions.
        '''
        super().__init__()
        self._functions = functions

    @classmethod
    def combine(cls, *funcs):
        '''Merge chains; i.e., combine all FunctionChains in `funcs` into a single FunctionChain.
        '''
        new_funcs = []
        for f in funcs:
            if isinstance(f, FunctionChain):
                new_funcs.extend(f.functions)
            else:
                new_funcs.append(f)
        return cls(tuple(new_funcs))

    @inject_call_state
    def __call__(self, *args, **kwargs):
        f_iter = iter(self._functions)
        result = next(f_iter)(*args, **kwargs)
        for f in f_iter:
            result = f(result, **kwargs)
        return result

    def __repr__(self):
        return f'{self.__class__.__name__}({self.functions})'

    def __str__(self):
        return f'({" | ".join(str(f) for f in self.functions)})'


class FunctionMerge(MetaFunction):
    _character_to_operator = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }
    _operator_to_character = {v: k for k, v in _character_to_operator.items()}

    def __init__(self, merge_func:tp.Callable, functions:tuple, join_str=None):
        '''A FunctionMerge merges its functions by executing all of them and passing their results to `merge_func`

        Args:
            join_str: If you're using a `merge_func` that is not one of the standard operator
            functions, use this argument to provide a custom character to use in string formatting. If not provided, we default to using str(merge_func).
        '''
        super().__init__()
        self._merge_func = merge_func
        self._functions = functions
        self._join_str = join_str or self._operator_to_character.get(
                merge_func, str(merge_func))

    @inject_call_state
    def __call__(self, *args, **kwargs):
        results = (f(*args, **kwargs) for f in self.functions)
        return self._merge_func(*results)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._merge_func}, {self.functions})'

    def __str__(self):
        func_str = f' {self._join_str} '.join(str(f) for f in self.functions)
        return f"({func_str})"


class SimpleFunction(MetaFunction):
    def __init__(self, function, print_location_in_traceback=True):
        '''A MetaFunction-aware wrapper around a single function
        The `bind` parameter causes us to pass a meta object as the first argument to our inherited function, but it is only respected if the wrapped function is not another metafunction.
        '''
        super().__init__()
        self._function = function
        self.add_location_to_traceback = print_location_in_traceback

        # An interesting side effect of wraps: it causes simplefunctions to collapse into each
        # other. Because calling wraps on a function copies all that function's attributes to the
        # new function, we copy _function, etc from the wrapped function. Essentially
        # absorbing it. I'm not sure if that's good or bad.
        functools.wraps(function)(self)

    @inject_call_state
    def __call__(self, *args, call_state, **kwargs):
        call_state._called_functions.append(self)
        if getattr(self._function, '_receives_call_state', False):
            args = (call_state, ) + args
        try:
            return self._function(*args, **kwargs)
        except Exception as e:
            self._handle_exception(call_state, e)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.functions[0]})'

    def __str__(self):
        return self.__name__

    @property
    def functions(self):
        return (self._function, )

    def _handle_exception(self, meta, e):
        if self.add_location_to_traceback:
            from metafunctions.util import highlight_current_function
            detailed_message = str(e)
            if meta:
                detailed_message = f"{str(e)} \n\nOccured in the following function: {highlight_current_function(meta)}"
            raise type(e)(detailed_message).with_traceback(e.__traceback__)
        raise


class DeferredValue(SimpleFunction):
    def __init__(self, value):
        '''A simple Deferred Value. Returns `value` when called. Equivalent to lambda x: x.
        '''
        self._value = value
        self.__name__ = repr(value)

    def __call__(self, *args, **kwargs):
        return self._value

    @property
    def functions(self):
        return (self, )
