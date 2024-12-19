# TODO

- [TODO](#todo)
  - [I Highest Importance](#i-highest-importance)
  - [II Requires Research](#ii-requires-research)
  - [III Lowest Importance](#iii-lowest-importance)
  - [IV Doubts and Head Scratchers](#iv-doubts-and-head-scratchers)
  - [Latest Implementations \& Fixes](#latest-implementations--fixes)

## I Highest Importance

- [ ] CSV "import" currently overwrites the file :facepalm:
  - [ ] Convert the provided CSV to JSON. check if key exists, if not add it yada yada
  - [ ] Move it to intermediates

- [ ] Make an executable for Linux aswell
  - [x] Need the user to download ffmpeg binaries as `ffmpeg-python` is just a wrapper, should mention that in the readme

- [ ] Addition of `database_tools`
  - [x] Write a utility script to check if there are missing pairs
  - [x] `matcher.py`, helper script to make the switch from your old archive.
  - [ ] Script to migrate to youtubes metadata using previously created user metadata.
    - [ ] Use a headless browser to get links under Songs if it doesn't exist as a Song fallback to Video
      - `https://music.youtube.com/search?q=example+song`
  - [ ] Script to remove duplicate entries that only differ with the key.

- [ ] Provide the user with a fallback json that consists of replacement keys \(for the ID's that fail or preference\)
  - [ ] Use the dbtools utility to be written to prompt the user for the replacement key

- [x] Log unavailable videos into a file.
  - [ ] Could be better

- [ ] Exit and notify the user somehow when `yt-dlp` outputs `Sign in to confirm you’re not a bot. This helps protect our community.`
  - [x] Break download loop
  - [ ] Use an alternative?
    - Piped
    - [Invidious](https://github.com/grqz/yt-dlp-invidious)

## II Requires Research

- [ ] Find out how to launch gui without a console

- [ ] Find out if there is a better way to structure the CLI logic or make it more maintainable in general [click](https://click.palletsprojects.com/en/8.1.x/)?

- [ ] Do async downloading

- [ ] Find out if this output from `yt-dlp` affects anything `WARNING: [youtube] Failed to download m3u8 information: HTTP Error 429: Too Many Requests`

- [ ] Fetch lyrics and add them into `library.json`
  - Sources that RiMusic is using seems pretty solid.

- [ ] Write tests

- [ ] InnerTube

## III Lowest Importance

- [ ] Make settings interactable (e.g import the file named x)

- [ ] Log bad thumbnails
  - [ ] `hqdefault`
  - [ ] Ones that are available as `hqdefault` but aren't a square (`720x720`)
    - OpenCV hsl similiarity? the fills in those files aren't just 1 color last I tried & checked

- [ ] Remove quirky file finding method for the `temp` directory in `download` function as it's not required anymore?

- [ ] Allow the library file to have no artist & no title specified
  - Tell `yt-dlp` to automatically tag it
  - Make a function to fetch missing metadata?

- [x] Handle cover and music seperately in `downloader.py`
  - [ ] Better `return` values

- [ ] Replace `eyed3` with `mutagen`

- [ ] Rename `key` to `video_id`

- [ ] Write a better scrape algorithm, get album names properly this time.

- [ ] Add a function to delete files in `downloads` that aren't in `library.json`

- [ ] Add a function to delete entries in `library.json` that aren't in `downloads`

- [ ] Fetch metadata from YouTube instead of using the existing data

- [ ] Implement `yt-dlp --get-filename -o "%(uploader)s hsfOqb5r8m0VbV31 %(title)s" VIDEO_URL` for null artists, which is caused by ViMusic's search function returning empty

- [ ] Write `PermissionError` exceptions

- [ ] Some languages have characters that are indexed inside the latin alphabet and by default I think Python just looks for its unicode index, so fixing this

## IV Doubts and Head Scratchers

- [ ] Find something that doesn't disrupt the user's workflow while getting the `likesPage`
  - cookie injection with selenium?
  - undetected chromedriver?
  - user script?
  - maybe google provides user data? (lame)

- RiMusic database adds all artists text whereas parser just gets the first one
  - look into artists text and separate the text if it has a comma or an ampersand
    - while this is pretty easy to do it might produce false artist names
  - see if `yt-dlp` or InnerTune API can provide any information about this
  - leave it, the parsed data will never be perfect and require some manual changes for it to be pristine anyway

## Latest Implementations & Fixes

NOTE: These will be removed after a while.

- [x] Record any manual changes to songs ~~\[did do this, but it's instead checking if json has been manually edited\]~~
  - why did i do it for the json? probably i hadn't done the export import at that time and was doing something wacky
  - [x] Check the downloads directory if any of the song tags has been manually changed
    - If it is changed, update tags on `library.json`
      - Else skip

- [x] Break when there is no internet connection in download loop
  - ERROR: [youtube] Fj7SH-YfH6A: Failed to extract any player response; please report this issue on  <https://github.com/yt-dlp/yt-dlp/issues?q=> , filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U

- [x] Proper logging

- [x] Store logger printouts from each session

- [x] Improve debug prints,
  - [x] Change errors that are handled to warnings or something else

- [x] Make the entire project an executable that is usable with command line input with defaults if parameters aren't changed
  - [x] PyInstaller

- [x] Ignore user config, copy the `defaultConfig.yaml` if there isn't a config file yet.

- [x] Write intermediate functions, i.e functions that are chained together in `tkgui.py` right now to use them both in CLI&GUI

- [x] Give some use to CSV <-> JSON conversion functions
