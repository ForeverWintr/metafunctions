from functools import wraps

from function_pipe.meta_function import SimpleFunction



def pipe_node(function):
    return SimpleFunction(function)
