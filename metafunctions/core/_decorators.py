'''
Internal decorators that are applied to MetaFunction methods, not functions.
'''
from functools import wraps
from collections.abc import Callable


def binary_operation(method):
    '''Internal decorator to apply common type checking for binary operations'''
    @wraps(method)
    def binary_operation(self, other):
        if isinstance(other, Callable):
            new_other = self.make_meta(other)
        else:
            new_other = self.defer_value(other)
        return method(self, new_other)
    return binary_operation


def inject_call_state(call_method):
    '''Decorates the call method to insure call_state is present in kwargs, or create a new one.'''
    @wraps(call_method)
    def with_call_state(self, *args, **kwargs):
        kwargs.setdefault('call_state', self.new_call_state())
        return call_method(self, *args, **kwargs)
    return with_call_state


