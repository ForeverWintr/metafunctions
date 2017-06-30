'''This module adapts the MetaFunction interface to the function-pipe interface.
'''
import function_pipe as _fpn

from metafunctions.util import node

# PipeNode kwargs
PREDECESSOR_RETURN = _fpn.PREDECESSOR_RETURN
PREDECESSOR_PN = _fpn.PREDECESSOR_PN
PN_INPUT = _fpn.PN_INPUT
PN_INPUT_SET = {PN_INPUT}
PIPE_NODE_KWARGS = {PREDECESSOR_RETURN, PREDECESSOR_PN, PN_INPUT}

def pipe_node(_func=None):
    return node(func)


def pipe_kwarg_bind(*key_positions):
    def f(func):
        return func
    return f
