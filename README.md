Features
* Lets you put names & descriptions on your media
* Automatic scraping of metadata and sibling file coroboration to get dates and other information right
* Allows you to add tags to your media for sorting.
* Mass lossy compress your files using ffmpeg because Apple reasons

# Installation and usage
`pip install patalynn`
For evironments where pip gets angry at you because of an external package manager, its planned to have an installation other than pip for linux and windows. (Pyinstaller?)
## Usage
`patalynn path/to/your/media/dump/directory`

Example dump structure from an iOS device
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
The extension api will allow for plugins to be loaded at runtime. 
Uses include adding other managers or ui modifications

# Platforms
* Windows 10/11
### Future
* Most linux distros
* TiOS<sup>[1](#f1)</sup>
  
## Philosophy


<a name="f1">1</a>: This is only a joke until someone ports libVLC to the Z80 :)
