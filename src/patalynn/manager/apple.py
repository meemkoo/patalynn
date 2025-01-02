"""
They put assert statements in Python for a damm reason.
"""

from . import registered_manager, Manager, Config
from .. import __version__ as patalynn_version

import asyncio

import os
import json
import time
import base64
import hashlib
from pathlib import Path
from io import BytesIO
import gzip

from typing import Literal

CATVERSION = "0.0.1"
DELIMETER = '\\'
PATHSAFE = 'md\x00\a'
CHUNKSIZE = 100
IMAGE_BLOCK_LOAD_FACTOR = 50

def decom(inputBytes):
    """
    decompress the given byte array (which must be valid 
    compressed gzip data) and return the decoded text (utf-8).
    """
    bio = BytesIO()
    stream = BytesIO(inputBytes)
    decompressor = gzip.GzipFile(fileobj=stream, mode='r')
    while True:
        chunk = decompressor.read(8192)
        if not chunk:
            decompressor.close()
            bio.seek(0)
            return bio.read().decode("utf-8")
        bio.write(chunk)
    return None

def com(inputString: str):
    """
    read the given string, encode it in utf-8,
    compress the data and return it as a byte array.
    """
    bio = BytesIO()
    bio.write(inputString.encode("utf-8"))
    bio.seek(0)
    stream = BytesIO()
    compressor = gzip.GzipFile(fileobj=stream, mode='w')
    while True:  # until EOF
        chunk = bio.read(8192)
        if not chunk:  # EOF?
            compressor.close()
            return stream.getvalue()
        compressor.write(chunk)

async def relieve():
    await asyncio.sleep(0)

@registered_manager(name=f'{__name__}.Apple')
class Apple(Manager):
    def __init__(self, config: Config):
        self.config = config
        self.catalog_file = Path(config.root).joinpath(Path(config.catalog_file))
        self.media_pool_path = Path(config.root).joinpath(Path(config.media_pool))

        self.catalog = None

        self.selection = None
        self.selection_pointer = 0

        self.files = None
        self.catalog_meta = None
        self._cold = True

        self._event_hooks = {name: lambda _: print(f"Debug: uncaught event on {self}") for name in self.events}


    def _parse_name_to_data(self, name):
        tags = []
        zestid = False

        # TODO: Implement mime
        mime = "TODO" # magic.from_file(f"{self.media_pool_path}\\{name}", mime=True)

        # First part of filename which holds year & month info
        yyyymm_alpha = name.split(DELIMETER)[0]
        nodate_imgname = name.split(DELIMETER)[1]

        month = str(yyyymm_alpha)[4:-2]
        year = str(yyyymm_alpha)[:-4]

        stage_rawid = str(nodate_imgname).split('.')[0]
        stage_ftype = str(nodate_imgname).split('.')[1].lower()

        if stage_rawid[-1] == ')':
            zestid = stage_rawid[10:-1]
            stage_rawid = stage_rawid[:8]
            pass

        if len(stage_rawid) == 8:
            pass
        elif len(stage_rawid) == 9:
            stage_rawid = stage_rawid[:4] + stage_rawid[4+1:]
            tags.append('IS_E')
            pass
        else:
            raise Exception('Error')

        always_int = stage_rawid[4:]
        img_or_id = stage_rawid[:4]
        raw_id = always_int
        if img_or_id[3] != '_':
            raw_id = img_or_id+always_int
            pass

        with open(f"{self.media_pool_path}\\{name}", 'rb') as f:
            file_hash = base64.encodebytes(hashlib.file_digest(f, hashlib.md5).digest()).decode('ascii')

        return year, month, raw_id, tags, mime, stage_ftype, zestid, file_hash

    def __filter_by(self, fil: callable):
        e = self.refreshed_state

        def fun(variable):
            try:
                assert fil(variable[1])
                return True
            except Exception as err:
                return False

        out = {c[0]: c[1] for c in list(filter(fun, e.items()))}
        return out


    def _open_catalog_file(self):
        """ Name could be considered misleading,\n
            Reads/validates catalog file from disk 
            into memory"""
        # TODO: Logging
        if os.path.exists(self.catalog_file):
            with open(self.catalog_file, 'rb') as cf:
                data = json.loads(decom(cf.read()))
        else:
            with open(self.catalog_file, 'xb') as cf:
                data = {PATHSAFE: ['penicilliumexpansum', CATVERSION, time.time(), 0, time.time()]}
                cf.write(com(json.dumps(data, separators=(',', ':'), indent=None)))
        
        if PATHSAFE not in data:
            print("Error: Bad format catalog")
            quit(-1)
        elif data[PATHSAFE][1] != CATVERSION:
            print("Warning: Differing version in catalog")
        elif data[PATHSAFE][0] != 'penicilliumexpansum':
            print("Error: Differing format in catalog")
            quit(-1)

        self.catalog_meta = data[PATHSAFE]
        data.pop(PATHSAFE)
        self.catalog = data

    def _update_catalog_file(self):
        """ Saves in memory catalog file to disk """
        self.catalog_meta[4] = time.time()
        self.catalog.update({PATHSAFE: self.catalog_meta})
        with open(self.catalog_file, 'wb') as cf:
            cf.write(com(json.dumps(self.catalog, separators=(',', ':'), indent=None)))
        self.catalog.pop(PATHSAFE)


    async def sync(self):
        """ Does five things:
            1. Detects for untracked files and
            assimilates them into the in-memory catalog
            2. Saves catalog to disk 
            3. Updates list of raw file paths
            4. Sets `_cold` to False
            5. Ensures dangling entries are marked
            6. Sets target entry at `selection` & `selection_pointer`
        """
        if self._cold:
            self._open_catalog_file()

        # TODO: Logging
        print("Info: Not validating existing catalog entries beyond media existance check")

        files = []
        for dir, _, f_names in os.walk(self.media_pool_path):
            await relieve()
            for f in f_names:
                files.append(f"{dir.split('\\')[-1]}\\{f}")

        for entry in self.catalog:
            await relieve()
            if entry not in files:
                print("Warning: Dangling entry, may need to fix missing") # TODO: logging
                self.catalog[entry]["tags"].append("DANGLING")
        
        x = {k: {} for k in files if k not in self.catalog.keys()}
        print(f"Info: {len(x)} new entires found!") # TODO: logging, again

        for k,v in x.items():
            year, month, raw_id, gen_tags, mime, stage_ftype, zestid, file_hash = self._parse_name_to_data(k)
            building = {
                "mm": month,
                "yyyy": year,
                "mime": mime,
                "tags": {},
                "generated": gen_tags,
                "rawftype": stage_ftype,
                "rawid": raw_id,
                "zestid": zestid,
                "title": "No Title",
                "desc": "No Description",
                "processing_steps": {},
                "siblings": {},
                "id_name": f"{k}",
                "file_hash": file_hash,
                "file_path": f"{self.media_pool_path}\\{k}"
            }

            await relieve()

            v.update(building)
            print(f"Info: {k} filled out and added")

        self.catalog.update(x)
        self.catalog_meta[3] = len(self.catalog)-1

        self.files = [await asyncio.sleep(0, result=path) for path in self.catalog.keys()]


        self._update_catalog_file()
        print(f"Info: Sunk Apple media manager on {patalynn_version=}")
        print(f"Info: Sunk with catalog file version {CATVERSION}")
        if self._cold:
            self.goto_media(self.selection_pointer)
            self._cold = False
            self.trigger_event("onWarm")


    def info(self):
        return {self}

    def goto_media(self, id: str | int):
        """ Jumps `selection` to `id`\n
            When `id` is an `int` it uses the `files` list to get the path.\n
            When `id` is a `str` its excpects a relative path. Ex: '202301__\\IMG_3618.JPG'
        """
        if isinstance(id, str):
            self.selection = self.catalog[id]
        elif isinstance(id, int):
            self.selection = self.catalog[self.files[id]]

    def switch_media(self, dir: Literal[-1, 1]=1):
        """ Increases or decreases `selection_pointer` and changes `selection`
        accordingly """
        if self.selection_pointer + dir == len(self.files):
            self.selection_pointer = 0
        elif self.selection_pointer + dir == -1:
            self.selection_pointer = len(self.files)-1
        else:
            self.selection_pointer += dir
        self.goto_media(self.selection_pointer)

    def current(self):
        return Path(self.selection["file_path"])

    def tag(self, tag: str, data=None):
        """ Adds `tag` with its `data` to the current selection. \n
            `tag` must be alphanumeric and != None 
        """
        assert self.selection, "Cant tag None"
        assert tag.isalnum() and tag
        tags: dict = self.selection["tags"]
        tags.update({tag: data})

    def deltag(self, tag: str):
        """ Removes `tag` from the current selections tags"""
        assert self.selection, "Cant tag None"
        assert tag.isalnum() and tag
        tags: dict = self.selection["tags"]
        try:
            tags.pop(tag)
        except Exception as _:
            pass


    def trigger_event(self, name, *args, **kwargs):
        self._event_hooks[name](*args, **kwargs)

    def add_event_hook(self, name, func):
        if name in self._event_hooks:
            self._event_hooks[name] = func
        else:
            raise Exception(f"No event called {name}")
