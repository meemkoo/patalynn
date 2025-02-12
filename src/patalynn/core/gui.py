# Copyright (C) 2025  Arsenic Vapor
# patalynn is a file viewer/manager targeted for use with iOS media dumps

from .. import __version__, __licence__
from ..manager import Manager, get_manager, Config

import tkinter as tk
from PIL import Image, ImageTk
import os
import vlc
from pathlib import Path
import webbrowser
import sys
from threading import Thread

from typing import Literal, Any, Callable, Generator

from multiprocessing import Queue


hottagkeymap = {
    "L": "reviewlater"
}


class Player:
    def __init__(self, parent: tk.Tk, backend: Manager, debug=False):
        self.backend = backend
        self.root = parent
        self.debug = debug

        self.videoLength = 0
        self.fullScreenState = False
        self.muted = False
        self.playing = False
        self.status = {}
        self.statusunclean = True

        self._done_queue = Queue()
        self._running_tasks = {}

        self._ref = {}

        self.init_vlc()
        self.init_widgets()
        self.events()

        self.update_status("Manager", "Awaiting sync")

    def init_vlc(self):
        self.vlcInstance: vlc.Instance = vlc.Instance()#["--aout=waveout"])
        self.mediaPlayer: vlc.MediaPlayer = self.vlcInstance.media_player_new()
        self.mediaPlayer.pause()

    def init_widgets(self):
        """ No like seriously this function is doing too much """
        self.videoPanel = tk.Frame(self.root)
        self.video_canvas = tk.Canvas(self.videoPanel, height=300, width=300, bg='#000000', highlightthickness=0)

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
            filewin.bind('<Key>', lambda e: filewin.destroy() if e.keysym == "Escape" else None)
            filewin.resizable(0,0)
            filewin.focus_force()
            filewin.transient(self.root)

            lshown = [False]
            h = tk.Scrollbar(filewin, orient = 'horizontal')
            # h.pack(side = tk.BOTTOM, fill = tk.X)
            v = tk.Scrollbar(filewin)
            # v.pack(side = tk.RIGHT, fill = tk.Y)
            t = tk.Text(filewin, wrap = tk.NONE,
                    xscrollcommand = h.set, 
                    yscrollcommand = v.set)
            t.insert(1.0, __licence__)
            t.config(state=tk.DISABLED)
            # t.pack(side=tk.TOP, fill=tk.X)
            h.config(command=t.xview)
            v.config(command=t.yview)

            def toggle():
                lshown[0] = not lshown[0]
                if lshown[0]:
                    h.pack_forget()
                    v.pack_forget()
                    t.pack_forget()
                else:
                    h.pack(side = tk.BOTTOM, fill = tk.X)
                    v.pack(side = tk.RIGHT, fill = tk.Y)
                    t.pack(side=tk.TOP, fill=tk.X)

            text1 = tk.Label(filewin, text="https://github.com/meemkoo", fg="blue", cursor="hand2")
            text1.bind("<Button-1>", lambda _: webbrowser.open("https://github.com/meemkoo"))
            text1.pack(padx=20, pady=12)

            text2 = tk.Label(filewin, text=f"Licence", fg="blue", cursor="hand2")
            text2.bind("<Button-1>", lambda _: toggle())
            text2.pack(padx=20, pady=12)

        f = tk.Menu(m, tearoff=0)
        f.add_command(label="New", command=donothing)
        f.add_command(
            label="Sync Manager", 
            command=self.future(self.backend.sync, self.onBackendTasks))


        e = tk.Menu(m, tearoff=0)
        e.add_command(label="Undo", command=donothing)

        m.add_cascade(label="File", menu=f)
        m.add_cascade(label="Settings", menu=e)
        m.add_command(label="About", command=about)

        self.root.config(menu=m)


    def update_status(self, item, value):
        self.status[item] = value#
        self.statusunclean = True

    def future(self, 
               work_callback, task_generator):
        tasks: Generator = task_generator()
        name = f"__{id(work_callback)}_{hash(work_callback)}_{work_callback.__name__}__"
        def work():
            output = work_callback()
            f = lambda: tasks.send(output)
            self._ref.update({name: f})
            self._done_queue.put((name, output))
            self._running_tasks.pop(name)

        def wrapper():
            next(tasks)
            self._running_tasks.update({name})
            t = Thread(target=work)
            t.start()
        return wrapper
        
    def requires_state(self, variable: bool):
        pass

    def events(self):
        self.root.bind('<space>', self.onPlayPause)
        self.root.bind('<Left>', self.onScrub)
        self.root.bind('<Right>', self.onScrub)
        self.root.bind('<m>', self.onMuteUnmute)
        self.root.bind('<Up>', self.onVolume)
        self.root.bind('<Down>', self.onVolume)
        # self.root.bind('<s>', self.future(self.backend.sync,
        #                                   lambda _: print(_)))

        self.root.bind('<Shift-Left>', lambda _: self.onSwitch(_, -1))
        self.root.bind('<Shift-Right>', lambda _: self.onSwitch(_, 1))

        for k,v in hottagkeymap.items():
            self.root.bind(f"<{k}>", lambda _: self.onHotTag(v))
            self.root.bind(f"<Shift-{k}>", lambda _: self.onHotTag(v, True))

        self.root.protocol('WM_DELETE_WINDOW', self.exit)


        # self.backend.add_event_hook("onWarm", self.onBackendReady)


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

    def onBackendTasks(self):
        self.update_status("Manager", "Loading...")
        event_data = yield
        print(event_data)
        # self.video = self.backend.current()
        # self._reset(self.video)
        # self.tag_bar.config(text=self.backend.selection["tags"])
        self.update_status("Manager", "Ready!")
        yield
        # return

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
            # self.backend.switch_media(dir)
            # self.video = self.backend.current()
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

    def exit(self):
        print("Info: Closing and syncing")
        self.mediaPlayer.stop()
        self.vlcInstance = None
        while self._running_tasks: pass # TODO: Make this better
        self.root.quit()
        self.root.destroy()

    def mainloop(self):
        while True:
            self.root.update()

            if not self._done_queue.empty():
                ev = self._done_queue.get(False)
                self._ref[ev[0]]() # TODO: Make this something thats not just a dict

            if self.statusunclean:
                text = ', '.join([f"{k}: {v}" for k,v in self.status.items()])
                self.status_label.config(text=text)
                self.statusunclean = False


def gmain(debug: bool=False):
    conf = Config.from_file(path=Path(f"{sys.argv[1]}/config.json"))
    manager = get_manager(conf.manager)

    player = Player(tk.Tk(), manager(conf), debug=debug)
    player.mainloop()

