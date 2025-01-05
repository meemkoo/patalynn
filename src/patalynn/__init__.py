# Copyright (C) 2025  Arsenic Vapor
# patalynn is a file viewer/manager targeted for use with iOS media dumps

__version__ = "0.0.2"

install_root = __file__

from .core import gui

def main(debug: bool=False):
    print("Error: Hello World!") # TODO: UGGGGHHHH LOGGING+NEVER GONNA HAPPEN
    gui.gmain(debug)
