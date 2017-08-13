'''Utilities for working with MetaFunctions'''
import os
import sys
import re
import contextlib

import colors

from metafunctions.core import CallState

def _system_supports_color():
    """
    Returns True if the running system's terminal supports color, and False otherwise. Originally
    from Django, by way of StackOverflow: https://stackoverflow.com/a/22254892/1286571
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


def highlight_current_function(call_state, color=colors.red, use_color=_system_supports_color()):
    '''Return a formatted string showing the location of the most recently called function in
    call_state.

    Consider this a 'you are here' when called from within a function pipeline.
    '''
    last_called_f = call_state._meta_stack[-1]
    current_name = str(last_called_f)

    # how many times will current_name appear in str(call_state._meta_entry)?
    # Bearing in mind that previous function names may contain current_name
    #num_occurences = sum(str(f).count(current_name) for f in call_state._called_functions)
    num_occurences = str(call_state._meta_entry).count(current_name)
    times_called = len([f for f in call_state._meta_stack if f is last_called_f])

    # There's probably a better regex for this.
    regex = f"((?:.*?{current_name}.*?){{{num_occurences-1}}}.*?){current_name}(.*$)"

    highlighted_name = f'->{current_name}<-'
    if use_color:
        highlighted_name = color(highlighted_name)

    highlighted_string = re.sub(regex, fr'\1{highlighted_name}\2', str(call_state._meta_entry))
    return highlighted_string


@contextlib.contextmanager
def traceback_from_call_state(call_state=None):
    '''This context manager monitors a call_state for exceptions, and attaches a message detailing the location of the exception to any traceback raised by that call_state.
    '''
    if call_state is None:
        call_state = CallState()

    try:
        yield call_state
    except Exception as e:
        detailed_message = str(e)
        detailed_message = f"{str(e)} \n\nOccured in the following function: {highlight_current_function(call_state)}"
        new_e = type(e)(detailed_message).with_traceback(e.__traceback__)
        raise new_e

