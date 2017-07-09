'''
Utility functions for use in function pipelines.
'''
import sys
import re
import functools

import colors

from metafunctions.core import MetaFunction
from metafunctions.core import SimpleFunction
from metafunctions.core import FunctionMerge
from metafunctions.concurrent import ConcurrentMerge


def node(_func=None, *, bind=False, modify_tracebacks=True):
    '''Turn the decorated function into a MetaFunction.

    Args:
        _func: Internal use. This will be the decorated function if node is used as a decorator
        with no params.
        bind: If True, the MetaFunction object is passed to the function as its first parameter.
        modify_tracebacks: If true, exceptions raised in composed functions have a string appended
        to them describing the location of the function in the function chain.

    Usage:

    @node(bind=True)
    def f(metafunc, x):
       <do something cool>
    '''
    def decorator(function):
        newfunc = SimpleFunction(function, bind, modify_tracebacks)
        return newfunc
    if not _func:
        return decorator
    return decorator(_func)


def bind_call_state(_func):
    def call_state_provider(*args, **kwargs):
        call_state = kwargs.pop('call_state')
        return _func(call_state, *args)


def store(key):
    '''Store the received output in the meta data dictionary under the given key.'''
    @node(bind=True)
    def store(meta, val):
        meta.data[key] = val
        return val
    store.__name__ = f"store('{key}')"
    return store


def recall(key, from_meta:MetaFunction=None):
    '''Retrieve the given key from the meta data dictionary. Optionally, use `from_meta` to specify
    a different metafunction than the current one.
    '''
    @node(bind=True)
    def recall(meta, val):
        if from_meta:
            return from_meta.data[key]
        return meta.data[key]
    recall.__name__ = f"recall('{key}')"
    return recall


def concurrent(function: FunctionMerge) -> ConcurrentMerge:
    '''Upgrade the specified FunctionMerge object to a ConcurrentMerge, which runs each of its
    component functions in separate processes. See ConcurrentMerge documentation for more
    information.

    Usage:

    c = concurrent(long_running_function + other_long_running_function)
    c(input_data) # The two functions run in parallel
    '''
    return ConcurrentMerge(function)


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


def highlight_current_function(meta, color=colors.red, use_color=_system_supports_color()):
    '''Return a formatted string showing the location of the currently active function in meta.

    Consider this a 'you are here' when called from within a function pipeline.
    '''
    current_name = str(meta._called_functions[-1])

    # how many times will current_name appear in str(meta)?
    # Bearing in mind that pervious function names may contain current_name
    num_occurences = sum(str(f).count(current_name) for f in meta._called_functions)

    # There's probably a better regex for this.
    skip = f'.*{current_name}'
    regex = f"((?:.*?{current_name}.*?){{{num_occurences-1}}}.*?){current_name}(.*$)"

    highlighted_name = f'->{current_name}<-'
    if use_color:
        highlighted_name = color(highlighted_name)

    highlighted_string = re.sub(regex, fr'\1{highlighted_name}\2', str(meta))
    return highlighted_string


