import six
import os
import re

from pyfiglet import figlet_format

try:
    from termcolor import colored
except ImportError:
    colored = None


def script_relative_path(file_path):
    '''
    Useful for testing with local files. Use a path relative to where the
    test resides and this function will return the absolute path
    of that file. Otherwise it will be relative to script that
    ran the test

    Note this is expensive performance wise so if you are calling this many
    times you may want to call it once and cache the base dir.
    '''
    # from http://bit.ly/2snyC6s

    import inspect
    scriptdir = inspect.stack()[1][1]
    return os.path.join(os.path.dirname(os.path.abspath(scriptdir)), file_path)


def cli_message(string, color=None, font="big", figlet=False):
    if colored:
        if not figlet:
            if color:
                six.print_(colored(string, color))
            else:
                mod_string = re.sub(
                    "<clickable>(.*?)</clickable>",
                    colored("\g<1>", "blue"),
                    string
                )
                six.print_(mod_string)
        else:
            if color:
                six.print_(colored(figlet_format(string, font=font), color))
            else:
                six.print_(figlet_format(string, font=font))

    else:
        six.print_(string)
