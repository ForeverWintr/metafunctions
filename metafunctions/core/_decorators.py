'''
Internal decorators for use in MetaFunction construction.
'''
import functools

from metafunctions.util import highlight_current_function
from ._exceptions import MetaFunctionError

def binary_operation(method):
    '''Internal decorator to apply common type checking for binary operations'''
    @functools.wraps(method)
    def binary_operation(self, other):
        if isinstance(other, Callable):
            new_other = self.make_meta(other)
        else:
            new_other = self.defer_value(other)
        return method(self, new_other)
    return binary_operation


def raise_with_location(method):
    '''
    Wrap the given method in an exception handler that intercepts exceptions to add information
    about where in the function pipeline they occured. Note that for this to work, the outer
    function in the function must be present as kwargs['meta'].
    '''
    @functools.wraps(method)
    def new_call(self, *args, **kwargs):
        try:
            method(*args, **kwargs)
        except Exception as e:
            detailed_message = ""


    return new_call
