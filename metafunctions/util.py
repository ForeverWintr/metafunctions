'''
Utility functions for use in function pipelines.
'''
from metafunctions.decorators import node
from metafunctions.core import MetaFunction


def store(key):
    '''Store the received output in the meta data dictionary under the given key.'''
    @node(bind=True)
    def f(meta, val):
        meta.data[key] = val
        return val
    return f


def recall(key, from_meta:MetaFunction=None):
    '''Retrieve the given key from the meta data dictionary. Optionally, use `from_meta` to specify
    a different metafunction than the current one.
    '''
    @node(bind=True)
    def f(meta, val):
        if from_meta:
            return from_meta.data[key]
        return meta.data[key]
    return f
