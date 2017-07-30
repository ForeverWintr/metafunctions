'''
Utility functions for use in function pipelines.
'''
import sys
import re
import functools
import typing as tp

import colors

from metafunctions.core import MetaFunction
from metafunctions.core import SimpleFunction
from metafunctions.core import FunctionMerge
from metafunctions.core import CallState
from metafunctions.concurrent import ConcurrentMerge
from metafunctions.map import MergeMap
from metafunctions import operators


def node(_func=None, *, name=None, modify_tracebacks=True):
    '''Turn the decorated function into a MetaFunction.

    Args:
        _func: Internal use. This will be the decorated function if node is used as a decorator
        with no params.
        modify_tracebacks: If true, exceptions raised in composed functions have a string appended
        to them describing the location of the function in the function chain.

    Usage:

    @node
    def f(x):
       <do something cool>
    '''
    def decorator(function):
        newfunc = SimpleFunction(function, name=name, print_location_in_traceback=modify_tracebacks)
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
    @node(name=f'star{fname}' if fname.startswith('(') else f'star({meta_function!s})')
    @functools.wraps(meta_function)
    def wrapper(args, **kwargs):
        return meta_function(*args, **kwargs)
    return wrapper


def store(key):
    '''Store the received output in the meta data dictionary under the given key.'''
    @node(name=f"store('{key}')")
    @bind_call_state
    def store(call_state, val):
        call_state.data[key] = val
        return val
    return store


def recall(key, from_call_state:CallState=None):
    '''Retrieve the given key from the meta data dictionary. Optionally, use `from_call_state` to
    specify a different call_state than the current one.
    '''
    @node(name=f"recall('{key}')")
    @bind_call_state
    def recall(call_state, val):
        if from_call_state:
            return from_call_state.data[key]
        return call_state.data[key]
    return recall


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
    as per the builtin `map` (https://docs.python.org/3.6/library/functions.html#map)
    '''
    return MergeMap(function, operator)

def _system_supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


def highlight_current_function(call_state, color=colors.red, use_color=_system_supports_color()):
    '''Return a formatted string showing the location of the currently active function in call_state.

    Consider this a 'you are here' when called from within a function pipeline.
    '''
    current_name = str(call_state._called_functions[-1])

    # how many times will current_name appear in str(call_state._meta_entry)?
    # Bearing in mind that pervious function names may contain current_name
    num_occurences = sum(str(f).count(current_name) for f in call_state._called_functions)

    # There's probably a better regex for this.
    skip = f'.*{current_name}'
    regex = f"((?:.*?{current_name}.*?){{{num_occurences-1}}}.*?){current_name}(.*$)"

    highlighted_name = f'->{current_name}<-'
    if use_color:
        highlighted_name = color(highlighted_name)

    highlighted_string = re.sub(regex, fr'\1{highlighted_name}\2', str(call_state._meta_entry))
    return highlighted_string


