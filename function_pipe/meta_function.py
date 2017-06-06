import functools
import operator
from collections.abc import Callable
import typing as tp
import abc


class MetaFunction(abc.ABC):
    '''A MetaFunction is a function that contains other functions. When executed, it calls the
    functions it contains.
    '''

    @abc.abstractmethod
    def __call__(self, arg):
        '''Call the functions contained in this MetaFunction'''

    @property
    def functions(self):
        return self._functions

    @classmethod
    def make_meta(cls, function):
        '''Wrap the given function in a metafunction, unless it's already a metafunction'''
        if not isinstance(function, MetaFunction):
            return SimpleFunction(function)
        return function

    def binary_operation(method):
        '''Internal decorator to apply common type checking for binary operations'''
        @functools.wraps(method)
        def binary_operation(self, other):
            new_other = other
            if not isinstance(other, Callable):
                new_other = lambda *args, **kwargs: other
            return method(self, self.make_meta(new_other))
        return binary_operation


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
    def __mul__(self, other):
        asdf

    # This is almost definitely a bad idea, but it's interesting that it works
    del binary_operation


class FunctionChain(MetaFunction):
    def __init__(self, functions:tuple):
        '''A FunctionChain is a metafunction that calls its functions in sequence, passing the
        results of the first function subsequent functions.
        '''
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
        f_iter = iter(self._functions)
        result = next(f_iter)(*args, **kwargs)
        for f in f_iter:
            result = f(result)
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
    _operator_to_format = {f: f'{{}} {c} {{}}' for c, f in _character_to_operator.items()}

    def __init__(self, merge_func:tp.Callable, functions:tuple, format_string=None):
        '''A FunctionMerge merges its functions by executing all of them and passing their results to `merge_func`

        Args:
            format_string: If you're using a `merge_func` that is not one of the standard operator
            functions, use this argument to provide a custom format string.
        '''
        self._merge_func = merge_func
        self._functions = functions
        self._format = self._operator_to_format[merge_func].format
        if format_string:
            self._format = format_string.format

    def __call__(self, *args, **kwargs):
        results = (f(*args, **kwargs) for f in self.functions)
        return self._merge_func(*results)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._merge_func}, {self.functions})'

    def __str__(self):
        return f'({self._format(*(str(f) for f in self.functions))})'


class SimpleFunction(MetaFunction):
    def __init__(self, function):
        '''A MetaFunction-aware wrapper around a single function'''
        self._function = function

        # This works!!!!
        functools.wraps(function)(self)

    def __call__(self, *args, **kwargs):
        return self._function(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._function})'

    def __str__(self):
        return self.__name__

    @property
    def functions(self):
        return (self._function, )

