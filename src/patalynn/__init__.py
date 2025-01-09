"""Copyright (C) 2025  Arsenic Vapor
patalynn is a file viewer/manager targeted for use with iOS media dumps

"""

__version__ = "0.0.2"

from .core import gui
import sys

def main(debug: bool=False):
    if debug:
        sys.modules[__name__].__dict__["__licence_path__"] = licence_file
        sys.modules[__name__].__dict__["__licence__"] = open(licence_file, 'r').read()

    print(__doc__.split('\n\n')[0])
    print("Error: Hello World!")
    gui.gmain(debug)
