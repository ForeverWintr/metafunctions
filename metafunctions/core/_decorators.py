'''
Internal decorators
'''
import functools
from collections.abc import Callable


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
