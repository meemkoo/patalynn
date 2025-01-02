""" Provides """

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from importlib import import_module


@dataclass
class Config:
    catalog_file: Path = ".\\mdb.json"
    media_pool: Path = ".\\media_pool"
    source_path: Path = ".\\source_pool"
    root: Path = ".\\mroot"
    manager: str = "patalynn.manager.apple.Apple"
    gui: bool = True
    verbose: bool = False

    @classmethod
    def from_file(cls, path: Path):
        with open(path, 'r') as cf:
            cfg = json.load(cf)
            if type(cfg) != dict:
                quit(-3)
        inst = cls.__new__(cls)
        inst.__init__(**cfg)
        return inst


def __error__(): raise AttributeError("Must be overloaded!")

class Manager: pass
    # _cold: bool
    # events = ["onWarm"]
    # selection: dict

    # def __init__(self) -> None: __error__()

    # def add_event_hook(self, name, func): __error__()

    # def trigger_event(self, name, *args, **kwargs): __error__()

    # def tag(self) -> None: __error__()

    # def deltag(self) -> None: __error__()

    # async def sync(self) -> None: __error__()

    # def switch_media(self, dir: Literal[-1, 1]=1) -> None: __error__()

    # def goto_media(self, id: str | int) -> None: __error__()

    # def tag(self, tag) -> None: __error__()

    # def current(self) -> Path: __error__()


_registered_managers = {}
def registered_manager(name: str):
    def inner(cls):
        _registered_managers.update({name: cls})
        return cls
    return inner

def get_manager(manager: str) -> type[Manager]:
    if manager in _registered_managers:
        return _registered_managers[manager]

    try:
        mod = import_module(f".{manager.split('.')[-2]}", __name__)
        return _registered_managers[manager]
    except ImportError as e:
        print(e)
        print("Not implemented yet :(")
        raise e
