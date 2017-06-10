'''
Utility functions for use in function pipelines.
'''
from . import decorators


def store(key):
    '''Store the received output in the meta data dictionary under the given key.'''
    def f(meta, val):
        meta[key] = val
        return val
    return f
