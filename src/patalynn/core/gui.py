from .. import __version__

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import vlc
from ..manager import Manager, get_manager, Config
from pathlib import Path
import webbrowser
import psutil
import sys

import asyncio

from typing import Literal


hottagkeymap = {
    "L": "reviewlater"
}


class Player:
    def __init__(self, parent: tk.Tk, backend: Manager, loop: asyncio.AbstractEventLoop, debug=False):
        self.backend = backend
        self.root = parent
        self.debug = debug
        self.loop = loop

        self.videoLength = 0
        self.fullScreenState = False
        self.muted = False
        self.playing = False
        self.status = {}
        self.statusunclean = True

        self.init_vlc()
        self.init_widgets()
        self.events()

        self.update_status("Manager", "No")

        self.tasks: list[asyncio.Task] = [loop.create_task(self.mainloop(1/120))]

    def init_vlc(self):
        self.vlcInstance: vlc.Instance = vlc.Instance()#["--aout=waveout"])
        self.mediaPlayer: vlc.MediaPlayer = self.vlcInstance.media_player_new()
        self.mediaPlayer.pause()

    def init_widgets(self):
        self.videoPanel = ttk.Frame(self.root)
        self.video_canvas = tk.Canvas(self.videoPanel, height=300, width=300, bg='#000000', highlightthickness=0)

        #Add image to the Canvas Items
        self.video_canvas.create_image(0,0,anchor=tk.SW,image=ImageTk.PhotoImage(Image.open("resources/loading.png")))

        self.video_canvas.pack(fill="both", expand=1)
        self.videoPanel.pack(fill="both", expand=1)
        
        self.panelid = self.videoPanel.winfo_id()
        self.mediaPlayer.set_hwnd(self.panelid)

        self.status_label = sl = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.tag_bar = tb = tk.Label(self.root, text="Tags:", bd=1, relief=tk.SUNKEN, anchor=tk.W)

        sl.pack(side=tk.BOTTOM, fill=tk.X)
        tb.pack(side=tk.BOTTOM, fill=tk.X)

        self.menu = m = tk.Menu(self.root)

        def donothing():
            filewin = tk.Toplevel(self.root)
            button = tk.Button(filewin, text="Do nothing button")
            button.pack()

        def about():
            filewin = tk.Toplevel(self.root)
            filewin.title("About")
            text = tk.Label(filewin, text="https://github.com/meemkoo", fg="blue", cursor="hand2")
            text.bind("<Button-1>", lambda _: webbrowser.open("https://github.com/meemkoo"))
            filewin.bind('<Key>', lambda e: filewin.destroy() if e.keysym == "Escape" else None)
            text.pack(padx=20, pady=12)
            filewin.resizable(0,0)
            filewin.focus_force()
            filewin.transient(self.root)

        f = tk.Menu(m, tearoff=0)
        f.add_command(label="New", command=donothing)
        f.add_command(label="Sync Manager", command=self.backend.sync)


        e = tk.Menu(m, tearoff=0)
        e.add_command(label="Undo", command=donothing)

        m.add_cascade(label="File", menu=f)
        m.add_cascade(label="Settings", menu=e)
        m.add_command(label="About", command=about)

        self.root.config(menu=m)

    def update_status(self, item, value):
        self.status[item] = value
        self.statusunclean = True

    def _inspection(self, _):
        print(psutil.cpu_percent())
        print(psutil.virtual_memory())


    def events(self):
        self.root.bind('<space>', self.onPlayPause)
        self.root.bind('<Left>', self.onScrub)
        self.root.bind('<Right>', self.onScrub)
        self.root.bind('<m>', self.onMuteUnmute)
        self.root.bind('<Up>', self.onVolume)
        self.root.bind('<Down>', self.onVolume)
        self.root.bind('<s>', lambda _: self.tasks.append(self.loop.create_task(self.backend.sync())))

        self.root.bind('<p>', self._inspection)

        self.root.bind('<Shift-Left>', lambda _: self.onSwitch(_, -1))
        self.root.bind('<Shift-Right>', lambda _: self.onSwitch(_, 1))

        for k,v in hottagkeymap.items():
            self.root.bind(f"<{k}>", lambda _: self.onHotTag(v))
            self.root.bind(f"<Shift-{k}>", lambda _: self.onHotTag(v, True))

        self.root.protocol('WM_DELETE_WINDOW', lambda _=0: self.loop.create_task(self.exit()))


        self.backend.add_event_hook("onWarm", self.onBackendReady)

    def onHotTag(self, name, delete=False):
        if not delete:
            c = self.backend.selection["tags"]
            if name in c:
                if c[name]:
                    self.backend.tag(name, False)
                    self.tag_bar.config(text=c)
                    return
            self.backend.tag(name, True)
        elif delete:
            self.backend.deltag(name)
        self.tag_bar.config(text=c)

    def onBackendReady(self):
        self.video = self.backend.current()
        self._reset(self.video)
        self.tag_bar.config(text=self.backend.selection["tags"])

    def onScrub(self, e):
        # v = self.mediaPlayer.audio_get_volume()
        print(self.mediaPlayer.get_position())
        
        # if e.keysym == 'Left' and v < 100:
        #     v += 5
        # elif e.keysym == 'Right' and v > 0:
        #     v -= 5
        # self.mediaPlayer.audio_set_volume(int(float(v)))
        # print(self.mediaPlayer.audio_get_volume())

    def onVolume(self, e: tk.Event):
        v = self.mediaPlayer.audio_get_volume()
        if e.keysym == 'Up' and v < 100:
            v += 5
        elif e.keysym == 'Down' and v > 0:
            v -= 5
        self.mediaPlayer.audio_set_volume(int(float(v)))
        # print(self.mediaPlayer.audio_get_volume())

    def onMuteUnmute(self, e=None):
        if self.muted:
            self.mediaPlayer.audio_set_mute(False)
            self.muted = False
        else:
            self.mediaPlayer.audio_set_mute(True)
            self.muted = True

    def onPlayPause(self, e=None):
        self.mediaPlayer.pause()
        if self.playing:
            self.playing = False
        else:
            self.playing = True

    def onSwitch(self, e=None, dir: Literal[-1, 1]=1):
        if not self.backend._cold:
            self.backend.switch_media(dir)
            self.video = self.backend.current()
            self._reset(self.video)
            self.tag_bar.config(text=self.backend.selection["tags"])
        else:
            self.update_status("Error", "initialize backend")

    def _reset(self, path):
        self.mediaPlayer.set_hwnd(self.panelid) # May not be neccesary
        if Path(path).exists():
            m = self.vlcInstance.media_new(os.path.expanduser(path))  # unicode
            self.mediaPlayer.set_media(m)
        self.mediaPlayer.play()
        self.root.after(60, self.mediaPlayer.pause)
        self.mediaPlayer.audio_set_mute(False)
        self.mediaPlayer.set_position(0.0)
        self.playing = False

    async def exit(self):
        print("Info: Closing and syncing")
        self.mediaPlayer.stop()
        self.vlcInstance = None
        self.root.quit()
        # self.tasks.append(self.loop.create_task(self.backend.sync())) # Perchance this will be something else
        # for task in self.tasks:
        await self.loop.create_task(self.backend.sync())
        # self.loop.run_until_complete()
        # self.loop.
        # asyncio.wait_for()
        self.loop.stop()
        self.root.destroy()

    async def mainloop(self, i):
        while True:
            self.root.update()
            if self.statusunclean:
                text = ', '.join([f"{k}: {v}" for k,v in self.status.items()])
                self.status_label.config(text=text)
                self.statusunclean = False
            await asyncio.sleep(i)


def gmain(debug: bool=False):
    conf = Config.from_file(path=Path(f"{sys.argv[1]}/config.json"))
    manager = get_manager(conf.manager)
    loop = asyncio.get_event_loop()
    player = Player(tk.Tk(), manager(conf), loop=loop, debug=debug)
    loop.run_forever()
    print("Info: all asyncio/threading is over")
