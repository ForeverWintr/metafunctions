from functools import wraps

from function_pipe.meta_function import MetaFunction



def pipe_node(function):
    mf = MetaFunction((function, ))
    mf = wraps(function)(mf)
    return mf
