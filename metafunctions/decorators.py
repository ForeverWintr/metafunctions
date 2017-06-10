from functools import wraps

from metafunctions.core import SimpleFunction


def node(_func=None, *, bind=False):
    '''Turn the decorated function into a MetaFunction.

    Args:
        _func: Internal use. This will be the decorated function if node is used as a decorator with no params.
        bind: If True, the MetaFunction object is passed to the function as its first parameter.

    Usage:

    @node(bind=True)
    def f(metafunc, x):
       <do something cool>
    '''
    if not _func:
        def decorator(function):
            return SimpleFunction(function, bind)
        return decorator
    return SimpleFunction(_func, bind)
