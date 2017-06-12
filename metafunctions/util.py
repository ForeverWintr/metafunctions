'''
Utility functions for use in function pipelines.
'''
import sys
import re

import colors

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


def system_supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


def highlight_current_function(meta, color=colors.red, use_color=system_supports_color()):
    '''Return a formatted string showing the location of the currently active function in meta.

    Consider this a 'you are here' when called from within a function pipeline.
    '''
    current_index = len(meta._called_functions)
    current_name = str(meta._called_functions[-1])

    # how many times will current_name appear in str(meta)?
    # Bearing in mind that pervious function names may contain current_name
    num_occurences = sum(str(f).count(current_name) for f in meta._called_functions)


    highlighted_name = f'->{current_name}<-'
    if use_color:
        highlighted_name = color(highlighted_name)

    regex = f'^((.*?{current_name}.*?){{{num_occurences-1}}}){current_name}'
    highlighted_string = re.sub(regex, fr'\1{highlighted_name}', str(meta))
    return highlighted_string


