'''
Utility functions for use in function pipelines.
'''
import sys
import re
import functools
import typing as tp
import os

import colors

from metafunctions.core import MetaFunction
from metafunctions.core import SimpleFunction
from metafunctions.core import FunctionMerge
from metafunctions.core import CallState
from metafunctions import util
from metafunctions.concurrent import ConcurrentMerge
from metafunctions.map import MergeMap
from metafunctions import operators


def node(_func=None, *, name=None):
    '''Turn the decorated function into a MetaFunction.

    Args:
        _func: Internal use. This will be the decorated function if node is used as a decorator
        with no params.

    Usage:

    @node
    def f(x):
       <do something cool>
    '''
    def decorator(function):
        newfunc = SimpleFunction(function, name=name)
        return newfunc
    if not _func:
        return decorator
    return decorator(_func)


def bind_call_state(func):
    @functools.wraps(func)
    def provides_call_state(*args, **kwargs):
        call_state = kwargs.pop('call_state')
        return func(call_state, *args, **kwargs)
    provides_call_state._receives_call_state = True
    return provides_call_state


def star(meta_function: MetaFunction) -> MetaFunction:
    '''
    star calls its Metafunction with *x instead of x.
    '''
    fname = str(meta_function)
    #This convoluted inline `if` just decides whether we should add brackets or not.
    @node(name=f'star{fname}' if fname.startswith('(') else f'star({fname})')
    @functools.wraps(meta_function)
    def wrapper(args, **kwargs):
        return meta_function(*args, **kwargs)
    return wrapper


def store(key):
    '''Store the received output in the meta data dictionary under the given key.'''
    @node(name=f"store('{key}')")
    @bind_call_state
    def storer(call_state, val):
        call_state.data[key] = val
        return val
    return storer


def recall(key, from_call_state:CallState=None):
    '''Retrieve the given key from the meta data dictionary. Optionally, use `from_call_state` to
    specify a different call_state than the current one.
    '''
    @node(name=f"recall('{key}')")
    @bind_call_state
    def recaller(call_state, val):
        if from_call_state:
            return from_call_state.data[key]
        return call_state.data[key]
    return recaller


def concurrent(function: FunctionMerge) -> ConcurrentMerge:
    '''
    Upgrade the specified FunctionMerge object to a ConcurrentMerge, which runs each of its
    component functions in separate processes. See ConcurrentMerge documentation for more
    information.

    Usage:

    c = concurrent(long_running_function + other_long_running_function)
    c(input_data) # The two functions run in parallel
    '''
    return ConcurrentMerge(function)


def mmap(function: tp.Callable, operator: tp.Callable=operators.concat) -> MergeMap:
    '''
    Upgrade the specified function to a MergeMap, which calls its single function once per input,
    as per the builtin `map` (https://docs.python.org/3.6/library/functions.html#map).

    Consider the name 'mmap' to be a placeholder for now.
    '''
    return MergeMap(MetaFunction.make_meta(function), operator)


def locate_error(meta_function: MetaFunction,
                 color=colors.red,
                 use_color=util.system_supports_color()) -> SimpleFunction:
    '''
    Wrap the given MetaFunction with an error handler that adds location information to any
    exception raised therein.

    Usage:
        cmp = locate_error(a | b | c)
        cmp()
    '''
    def with_location(*args, call_state, **kwargs):
        new_e = None
        try:
            return meta_function(*args, call_state=call_state, **kwargs)
        except Exception as e:
            if hasattr(e, 'location') and e.location:
                # If the exception has location info attached
                location = e.location
            else:
                location = call_state.highlight_active_function()

            if use_color:
                location = util.color_highlights(location)
            detailed_message = (f"{str(e)} \n\nOccured in the following function: {location}")
            new_e = type(e)(detailed_message).with_traceback(e.__traceback__)
            new_e.__cause__ = e.__cause__
        raise new_e
    with_location._receives_call_state = True
    return node(with_location, name=str(meta_function))
