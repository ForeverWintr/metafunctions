'''
Internal decorators that are applied to MetaFunction methods, not functions.
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


#def link_child_functions(call_method):
    #'''
    #Internal deocrator to initialize links to child functions pre-call, and remove them
    #post-call.
    #'''
    #@functools.wraps(call_method)
    #def new_call(self, *args, **kwargs):
        ##call link on each child function
        #for f in self.functions:
            #try:

        #pass


