"""Utilities for working with MetaFunctions"""
import os
import re
import sys

HIGHLIGHT_TEMPLATE = "->{}<-"


def red(string):
    """Wrap string in ANSI escape codes for red text"""
    return f"\033[31m{string}\033[0m"


def highlight(string):
    return HIGHLIGHT_TEMPLATE.format(string)


_color_regex = re.compile(HIGHLIGHT_TEMPLATE.format(".*?"))


def color_highlights(string):
    """Color all highlights red"""
    for substr in _color_regex.findall(string):
        string = string.replace(substr, red(substr))
    return string


def system_supports_color():
    """
    Returns True if the running system's terminal supports color, and False otherwise.

    A non-empty NO_COLOR environment variable disables color (https://no-color.org), and a
    non-empty FORCE_COLOR enables it. NO_COLOR takes precedence. Otherwise, color is off on
    Windows, and elsewhere is on only if stdout is a tty.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if sys.platform == "win32":
        return False
    # isatty is not always implemented
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def replace_nth(string, substring, occurance_index: int, new_substring):
    """Return string, with the instance of substring at `occurance_index` replaced with new_substring"""
    escaped = re.escape(substring)
    # There's probably a better regex for this.
    regex = f"((?:.*?{escaped}.*?){{{occurance_index - 1}}}.*?){escaped}(.*$)"
    return re.sub(regex, rf"\1{new_substring}\2", string)
