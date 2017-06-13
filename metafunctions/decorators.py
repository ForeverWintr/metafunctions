import functools


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
    from metafunctions.core import SimpleFunction
    if not _func:
        def decorator(function):
            return SimpleFunction(function, bind)
        return decorator
    return SimpleFunction(_func, bind)


def raise_with_location(method):
    '''
    Wrap the given method in an exception handler that intercepts exceptions to add information
    about where in the function pipeline they occured. Note that for this to work, the outer
    function in the function must be present as kwargs['meta'].

    SimpleFunction applies this decorator by default.
    '''
    @functools.wraps(method)
    def new_call(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            detailed_message = ""
            raise
    return new_call
