'''
Utility functions for use in function pipelines.
'''
import sys
import re
import functools

import colors

from metafunctions.core import MetaFunction
from metafunctions.core import SimpleFunction


def node(_func=None, *, bind=False, modify_tracebacks=True):
    '''Turn the decorated function into a MetaFunction.

    Args:
        _func: Internal use. This will be the decorated function if node is used as a decorator with no params.
        bind: If True, the MetaFunction object is passed to the function as its first parameter.

    Usage:

    @node(bind=True)
    def f(metafunc, x):
       <do something cool>
    '''
    def decorator(function):
        if modify_tracebacks:
            newfunc = raise_with_location(function)
        newfunc = SimpleFunction(newfunc, bind)
        return newfunc
    if not _func:
        return decorator
    return decorator(_func)


def store(key):
    '''Store the received output in the meta data dictionary under the given key.'''
    @node(bind=True)
    def f(meta, val):
        meta.data[key] = val
        return val
    return f


def recall(key, from_meta:MetaFunction=None):
    '''Retrieve the given key from the meta data dictionary. Optionally, use `from_meta` to specify
    a different metafunction than the current one.
    '''
    @node(bind=True)
    def f(meta, val):
        if from_meta:
            return from_meta.data[key]
        return meta.data[key]
    return f


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
    regex = f"((?:.*?{current_name}.*?){{{num_occurences-1}}}.*?)f(.*$)"

    highlighted_name = f'->{current_name}<-'
    if use_color:
        highlighted_name = color(highlighted_name)

    highlighted_string = re.sub(regex, fr'\1{highlighted_name}\2', str(meta))
    return highlighted_string


def raise_with_location(function):
    '''
    Wrap the given function in an exception handler that intercepts exceptions to add information
    about where in the function pipeline they occured. Note that for this to work, the outer
    function in the function must be present as kwargs['meta'].

    SimpleFunction applies this decorator by default.
    '''
    @functools.wraps(function)
    def new_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            meta = kwargs.get('meta')
            detailed_message = str(e)
            if meta:
                detailed_message = f"{str(e)} \n\n Occured in the following function: {highlight_current_function(meta)}"
            raise type(e)(detailed_message).with_traceback(e.__traceback__)
    return new_function

