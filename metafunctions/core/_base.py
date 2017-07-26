import operator
import typing as tp
import abc
import itertools
import functools


from metafunctions.core._decorators import binary_operation
from metafunctions.core._decorators import inject_call_state
from metafunctions.core._call_state import CallState
from metafunctions.operators import concat
from metafunctions import exceptions


class MetaFunction(metaclass=abc.ABCMeta):

    # Metafunctions will pass call state to any function with this attribute set to true
    _receives_call_state = True
    _function_join_str = ''

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        '''A MetaFunction is a function that contains other functions. When executed, it calls the
        functions it contains.
        '''
        self._functions = []

    @abc.abstractmethod
    def __call__(self, *args, call_state=None, **kwargs):
        '''Call the functions contained in this MetaFunction'''

    def __str__(self):
        return f'({f" {self._function_join_str} ".join(str(f) for f in self.functions)})'

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
    def __and__(self, other):
        return FunctionMerge.combine(concat, self, other)

    @binary_operation
    def __rand__(self, other):
        return FunctionMerge.combine(concat, other, self)

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

    @binary_operation
    def __matmul__(self, other):
        from metafunctions.util import star
        return FunctionChain.combine(self, star(other))

    @binary_operation
    def __rmatmul__(self, other):
        from metafunctions.util import star
        return FunctionChain.combine(other, star(self))


class FunctionChain(MetaFunction):
    _function_join_str = '|'
    def __init__(self, *functions):
        '''A FunctionChain is a metafunction that calls its functions in sequence, passing the
        results of the first function subsequent functions.
        '''
        super().__init__()
        self._functions = functions

    @inject_call_state
    def __call__(self, *args, **kwargs):
        f_iter = iter(self._functions)
        result = next(f_iter)(*args, **kwargs)
        for f in f_iter:
            result = f(result, **kwargs)
        return result

    def __repr__(self):
        return f'{self.__class__.__name__}{self.functions}'

    @classmethod
    def combine(cls, *funcs):
        '''Merge chains; i.e., combine all FunctionChains in `funcs` into a single FunctionChain.
        '''
        new_funcs = []
        for f in funcs:
            if type(f) is cls:
                new_funcs.extend(f.functions)
            else:
                new_funcs.append(f)
        return cls(*new_funcs)


class FunctionMerge(MetaFunction):
    _character_to_operator = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '&': concat,
    }
    _operator_to_character = {v: k for k, v in _character_to_operator.items()}

    def __init__(self, merge_func:tp.Callable, functions:tuple, function_join_str=''):
        '''
        A FunctionMerge merges its functions by executing all of them and passing their results to
        `merge_func`.

        Behaviour of __call__:

        FunctionMerge does not pass all positional arguments to all of its functions. Rather, given
        `f=FunctionMerge()` when f is called with `f(*args)`,

        * if len(args) == 1, each component function is called with args[0]
        * if len(args) > 1 <= len(functions), function n is called with arg n. Any remaining
        functions after all args have been exhausted are called with no args.
        * if len(args) < len(functions), a MetaFunction CallError is raised.

        Args:
            function_join_str: If you're using a `merge_func` that is not one of the standard operator
            functions, use this argument to provide a custom character to use in string formatting. If
            not provided, we default to using str(merge_func).
        '''
        super().__init__()
        self._merge_func = merge_func
        self._functions = functions
        self._function_join_str = function_join_str or self._operator_to_character.get(
                merge_func, str(merge_func))

    @inject_call_state
    def __call__(self, *args, **kwargs):
        args_iter, func_iter = self._get_call_iterators(args)

        results = []
        # Note that args_iter appears first in the zip. This is because I know its len is <=
        # len(func_iter) (I asserted so above). In zip, if the first iterator is longer than the
        # second, the first will be advanced one extra time, because zip has already called next()
        # on the first iterator before discovering that the second has been exhausted.
        for arg, f in zip(args_iter, func_iter):
            results.append(f(arg, **kwargs))

        #Any extra functions are called with no input
        results.extend([f(**kwargs) for f in func_iter])
        return self._merge_func(*results)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._merge_func}, {self.functions})'

    @classmethod
    def combine(cls, merge_func: tp.Callable, *funcs, function_join_str=None):
        '''Combine FunctionMerges. If consecutive FunctionMerges have the same merge_funcs, combine
        them into a single FunctionMerge.

        NOTE: combine does not check to make sure the merge_func can accept the new number of
        arguments, or that combining is appropriate for the operator. (e.g., it is inappropriate to
        combine FunctionMerges where order of operations matter. 5 / 2 / 3 != 5 / (2 / 3))
        '''
        new_funcs = []
        for f in funcs:
            if isinstance(f, cls) and f._merge_func == merge_func:
                new_funcs.extend(f.functions)
            else:
                new_funcs.append(f)
        return cls(merge_func, tuple(new_funcs), function_join_str=function_join_str)

    def _get_call_iterators(self, args):
        '''Do length checking and return (`args_iter`, `call_iter`), iterables of arguments and
        self.functions. Call them using zip. Note that len(args) can be less than
        len(self.functions), and remaining functions should be called with no argument.
        '''
        args_iter = iter(args)
        func_iter = iter(self.functions)
        if len(args) > len(self.functions):
            raise exceptions.CallError(
                    f'{self} takes 1 or <= {len(self.functions)} '
                    f'arguments, but {len(args)} were given')
        if len(args) == 1:
            args_iter = itertools.repeat(next(args_iter))

        return args_iter, func_iter


class SimpleFunction(MetaFunction):
    def __init__(self, function, name=None, print_location_in_traceback=True):
        '''A MetaFunction-aware wrapper around a single function
        The `bind` parameter causes us to pass a meta object as the first argument to our inherited function, but it is only respected if the wrapped function is not another metafunction.
        '''
        # An interesting side effect of wraps: it causes simplefunctions to collapse into each
        # other. Because calling wraps on a function copies all that function's attributes to the
        # new function, we copy _function, etc from the wrapped function. Essentially
        # absorbing it. I'm not sure if that's good or bad.
        functools.wraps(function)(self)

        super().__init__()
        self._function = function
        self.add_location_to_traceback = print_location_in_traceback
        self._name = name or getattr(function, '__name__', False) or str(function)

    @inject_call_state
    def __call__(self, *args, call_state, **kwargs):
        call_state._called_functions.append(self)
        if getattr(self._function, '_receives_call_state', False):
            kwargs['call_state'] = call_state
        try:
            return self._function(*args, **kwargs)
        except Exception as e:
            self._handle_exception(call_state, e)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.functions[0]!r})'

    def __str__(self):
        return self._name

    @property
    def functions(self):
        return (self._function, )

    def _handle_exception(self, call_state, e):
        if self.add_location_to_traceback:
            from metafunctions.util import highlight_current_function
            detailed_message = str(e)
            detailed_message = f"{str(e)} \n\nOccured in the following function: {highlight_current_function(call_state)}"
            raise type(e)(detailed_message).with_traceback(e.__traceback__)
        raise


class DeferredValue(SimpleFunction):
    def __init__(self, value):
        '''A simple Deferred Value. Returns `value` when called. Equivalent to lambda x: x.
        '''
        self._value = value
        self._name = repr(value)

    def __call__(self, *args, **kwargs):
        return self._value

    def __repr__(self):
        return f'{self.__class__.__name__}({self._value!r})'

    @property
    def functions(self):
        return (self, )
