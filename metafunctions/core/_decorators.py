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
        call_state = kwargs.setdefault('call_state', self.new_call_state())
        call_state._meta_stack.append(self)
        try:
            return call_method(self, *args, **kwargs)
        except Exception as e:
            call_state.set_exception(e)
            raise
        finally:
            call_state._meta_stack.pop()
    return with_call_state


