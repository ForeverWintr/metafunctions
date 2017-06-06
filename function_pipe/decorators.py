from functools import wraps

from function_pipe.metafunctions import SimpleFunction



def pipe_node(function):
    return SimpleFunction(function)
