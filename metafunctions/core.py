import functools
import operator
from collections.abc import Callable
import typing as tp
import abc


class MetaFunction(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        '''A MetaFunction is a function that contains other functions. When executed, it calls the
        functions it contains.
        '''
        self.data = {}
        self._called_functions = []

    @abc.abstractmethod
    def __call__(self, arg):
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

    def _binary_operation(method):
        '''Internal decorator to apply common type checking for binary operations'''
        @functools.wraps(method)
        def binary_operation(self, other):
            if isinstance(other, Callable):
                new_other = self.make_meta(other)
            else:
                new_other = self.defer_value(other)
            return method(self, new_other)
        return binary_operation

    def _modify_kwargs(self, kwargs: dict):
        '''Do pre-call modifications to the kwargs dictionary. Currently this just means adding a
        meta object if _bind is true.
        '''
        kwargs.setdefault('meta', self)

    ### Operator overloads ###
    @_binary_operation
    def __or__(self, other):
        return FunctionChain.combine(self, other)

    @_binary_operation
    def __ror__(self, other):
        return FunctionChain.combine(other, self)

    @_binary_operation
    def __add__(self, other):
        return FunctionMerge(operator.add, (self, other))

    @_binary_operation
    def __radd__(self, other):
        return FunctionMerge(operator.add, (other, self))

    @_binary_operation
    def __sub__(self, other):
        return FunctionMerge(operator.sub, (self, other))

    @_binary_operation
    def __rsub__(self, other):
        return FunctionMerge(operator.sub, (other, self))

    @_binary_operation
    def __mul__(self, other):
        return FunctionMerge(operator.mul, (self, other))

    @_binary_operation
    def __rmul__(self, other):
        return FunctionMerge(operator.mul, (other, self))

    @_binary_operation
    def __truediv__(self, other):
        return FunctionMerge(operator.truediv, (self, other))

    @_binary_operation
    def __rtruediv__(self, other):
        return FunctionMerge(operator.truediv, (other, self))

    # This is almost definitely a bad idea, but it's interesting that it works
    del _binary_operation


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

    def __call__(self, *args, **kwargs):
        self._modify_kwargs(kwargs)
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

    def __call__(self, *args, **kwargs):
        self._modify_kwargs(kwargs)
        results = (f(*args, **kwargs) for f in self.functions)
        return self._merge_func(*results)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._merge_func}, {self.functions})'

    def __str__(self):
        func_str = f' {self._join_str} '.join(str(f) for f in self.functions)
        return f"({func_str})"


class SimpleFunction(MetaFunction):
    def __init__(self, function, bind=False, print_location_in_traceback=False):
        '''A MetaFunction-aware wrapper around a single function'''
        super().__init__()
        self._bind = bind
        self._function = function
        self.add_location_to_traceback = print_location_in_traceback

        # This works!!!!
        functools.wraps(function)(self)

    def __call__(self, *args, **kwargs):
        meta = kwargs.pop('meta', self)
        meta._called_functions.append(self)
        additional_args = ()
        if self._bind:
            #If we've recieved a higher function's meta, pass it. Else pass self.
            additional_args = (meta, )
        try:
            return self._function(*additional_args, *args, **kwargs)
        except Exception as e:
            self._handle_exception(meta, e)

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
                detailed_message = f"{str(e)} \n\n Occured in the following function: {highlight_current_function(meta)}"
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
