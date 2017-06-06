from functools import wraps

from metafunctions.metafunctions import SimpleFunction



def pipe_node(function):
    return SimpleFunction(function)
