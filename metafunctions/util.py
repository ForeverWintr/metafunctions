'''Utilities for working with MetaFunctions'''
import os
import sys
import re
import contextlib

DEFAULT_HIGHLIGHT_COLOR = None
try:
    import colors
except ImportError:
    _HAS_COLORS = False
else:
    DEFAULT_HIGHLIGHT_COLOR = colors.red
    _HAS_COLORS = True

HIGHLIGHT_TEMPLATE = '->{}<-'

def highlight(string):
    return HIGHLIGHT_TEMPLATE.format(string)

_color_regex = re.compile(HIGHLIGHT_TEMPLATE.format('.*?'))
def color_highlights(string, color=DEFAULT_HIGHLIGHT_COLOR):
    '''Color all highlights'''
    for substr in _color_regex.findall(string):
        string = string.replace(substr, color(substr))
    return string

def system_supports_color():
    """
    Returns True if the running system's terminal supports color, and False otherwise. Originally
    from Django, by way of StackOverflow: https://stackoverflow.com/a/22254892/1286571
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not _HAS_COLORS or not supported_platform or not is_a_tty:
        return False
    return True


def replace_nth(string, substring, occurance_index: int, new_substring):
    '''Return string, with the instance of substring at `occurance_index` replaced with new_substring
    '''
    escaped = re.escape(substring)
    # There's probably a better regex for this.
    regex = f"((?:.*?{escaped}.*?){{{occurance_index-1}}}.*?){escaped}(.*$)"
    return re.sub(regex, fr'\1{new_substring}\2', string)


