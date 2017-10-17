'''
Internal decorators that are applied to MetaFunction methods, not functions.
'''
from functools import wraps
from collections.abc import Callable


def binary_operation(method):
    '''Internal decorator to apply common type checking for binary operations'''
    @wraps(method)
    def new_operation(self, other):
        if isinstance(other, Callable):
            new_other = self.make_meta(other)
        else:
            new_other = self.defer_value(other)
        return method(self, new_other)
    return new_operation


def manage_call_state(call_method):
    '''Decorates the call method to insure call_state is present in kwargs, or create a new one.
    If the call state isn't active, we assume we are the meta entry point.
    '''
    @wraps(call_method)
    def with_call_state(self, *args, **kwargs):
        try:
            call_state = kwargs['call_state']
        except KeyError:
            call_state = self.new_call_state()
            kwargs['call_state'] = call_state
        call_state.push(self)
        r = call_method(self, *args, **kwargs)
        call_state.pop()
        return r
    return with_call_state

