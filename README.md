# TODO
* Make all the markdown files look nicer
* Find a better way to do asyncio or threading then "spam `await asyncio.sleep()` in every loop ever as to not block the gui"
* LOGGING!!!
* Create a better (And stable!) Extension api (I honestly dont know what I was thinking with `switch_media()`)
* Following the above item, make the Manager class have less resposibilities
* Stop being lazy and get rid of the first-person pronouns in documentation such as this readme. The smiley faces stay though, profesionalisim be dammed.

A file viewer/manager targeted for use with iOS media dumps. 
Features
* Lets you put names & descriptions and your photos
* Automatic scraping of metadata and sibling file coroboration to get dates and other information right
* Allows you to add tags to your media for sorting and ...
* Mass lossy compress your files using ffmpeg because Apple

# Installation and usage
Will probably get on PyPi soon so you can use `pip install patalynn` in the future.
For now the releases should be configured with a `.whl` file

## Usage
`patalynn path/to/your/media/dump/directory`

Example dump structure from an apple shrapnel
```
dump_root
|- pool
|  |- 205001__
|  |  |- IMG_2452.JPG
|  |  |- IMG_E3621.JPG
|  |- 202501_a
|  |  |- RFWG2232.mp4
|- mdb.pexum
|- config.json
```

# Extension API
WIP!
The extension api allows developers to specify proporites of thier specific media pool as a Manager subclass.

# Platforms
The goals are to get Patalynn to run on 
* Windows 10/11
* Most Linux Distros
* TiOS[^1]
* Knightos[^1]
  
## MacOS / Philosophy
I will not be go out of my way to get the little quirky MacOS things (mainly regarding the GUI) to clutter up all the code. If you really want to contribute MacOS support, it will be done once the GUI code is seperated from the excplicitly Tkinter backend. This notice MUST remain until another builtin manager is added. This is because as it stands, the whole purpose of this project is to make dealing with iOS media dumps nicer as apple does some weird metadata things that I dont fully understand yet. Examples would include AAE files. Also Live photos. (Which android platforms might be doing now but thats not the point) Apple exports live photos as a video and image file which is reasonable. However it would be nice to copy both the video and the image at once, or select a different key frame, etc.

[^1] For those who need to here it this is a joke. At least until someone ports libVLC to the Z80 :)
