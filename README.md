# TODO
* Make all the markdown files look nicer
* Find a better way to do asyncio or threading then "spam `await asyncio.sleep()` in every loop ever as to not block the gui"
* LOGGING!!!

A file viewer/manager targeted for use with iOS media dumps. 
Features:
* (Will) Support extensions to work with more than just iOS media dumps. I really should add a flat one that just assumes no apple shrapnel. but whatever
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

