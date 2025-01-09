"""Copyright (C) 2025  Arsenic Vapor
patalynn is a file viewer/manager targeted for use with iOS media dumps

"""

__version__ = "0.0.2"

from . import licence
__licence__ = licence.__doc__

from .core import gui

def main(debug: bool=False):

    print(__doc__.split('\n\n')[0])
    print("Error: Hello World!")
    gui.gmain(debug)
