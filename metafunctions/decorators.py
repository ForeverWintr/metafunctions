from functools import wraps

from metafunctions.metafunctions import SimpleFunction



def pipe_node(function):
    return SimpleFunction(function)


def node(bind=False):
    '''Turn the decorated function into a MetaFunction.

    Args:
        bind: If True, the MetaFunction object is passed to the function as its first parameter.

    Usage:

    @node(bind=True)
    def f(metafunc, x):
       <do something cool>
    '''
    def decorator(function):
        return SimpleFunction(function, bind)
    return decorator
