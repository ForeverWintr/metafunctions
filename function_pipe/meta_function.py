import functools
import operator
from collections.abc import Callable
import typing as tp

class MetaFunction:
    def __init__(self, functions: tuple):
        '''A MetaFunction is a function that contains other functions. When executed, it calls the
        functions it contains.

        MetaFunctions can be composed with
        '''
        self._functions = functions

    def __call__(self, arg):
        result = arg
        for f in self._functions:
            result = f(result)
        return result

    @classmethod
    def make_meta(cls, function):
        '''Wrap the given function in a metaclass, unless it's already a metaclass'''
        if not isinstance(function, cls):
            return cls((function, ))
        return function

    def __repr__(self):
        return 'MetaFunction({})'.format(' | '.join((f.__name__ for f in self._functions)))

    def binary_operation(method):
        '''Internal decorator to apply common type checking for binary operations'''
        @functools.wraps(method)
        def binary_operation(self, other):
            new_other = other
            if not isinstance(other, Callable):
                new_other = lambda *args, **kwargs: other
            return method(self, self.make_meta(new_other))
        return binary_operation

    @binary_operation
    def __or__(self, other):
        return self.__class__(self._functions + other._functions)

    @binary_operation
    def __ror__(self, other):
        return self.__class__(other._functions + self._functions)

    ### Non composing operators ###
    @binary_operation
    def __add__(self, other):
        return self.__class__()

    @binary_operation
    def __mul__(self, other):
        asdf

    # This is almost definitely a bad idea, but it's interesting that it works
    del binary_operation


class FunctionTuple(tuple):
    _character_to_operator = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }
    _operator_to_format = {f: f'{{}} {c} {{}}' for c, f in _character_to_operator.items()}

    def __new__(cls, operator_func: tp.Callable, *funcs):
        if not operator_func in cls._operator_to_format:
            raise TypeError(f'Invalid operation argument. {operator_func} is not a member of {set(cls._operator_to_format)}')
        return tuple.__new__(cls, (operator_func,) + funcs)

    def __str__(self):
        return self._operator_to_format[self[0]].format(*self[1:])
