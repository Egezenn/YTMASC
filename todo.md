# TODO

- [TODO](#todo)
  - [I Working on](#i-working-on)
  - [II Highest Importance](#ii-highest-importance)
  - [III Requires Research](#iii-requires-research)
  - [IV Lowest Importance](#iv-lowest-importance)
  - [V Doubts and Head Scratchers](#v-doubts-and-head-scratchers)
  - [VI TK Gui Deprecation](#vi-tk-gui-deprecation)
  - [Latest Implementations \& Fixes](#latest-implementations--fixes)

## I Working on

- [ ] Proper logging
  - bumped up because code is unreadable with the previous *crappy* solution

## II Highest Importance

- [ ] Make an executable for Linux aswell

- [ ] Addition of `database_tools`
  - [x] Write a utility script to check if there are missing pairs
  - [x] `matcher.py`, helper script to make the switch from your old archive.
  - [ ] Script to migrate to youtubes metadata using previously created metadata.
  - [ ] Script to remove duplicate entries that only differ with the key.

- [ ] Manual editing logging
  - [ ] Use metadata from user data if key exists
    - [ ] Use fallback keys provided by user
  - [ ] Make use of database_tools' finder

- [x] Record any manual changes to songs \[did do this, but it's instead checking if json has been manually edited\]
  - [ ] Check the downloads directory if any of the song tags has been manually changed
    - If it is changed, update tags on `library.json`
      - Else skip
      - [ ] Or make the json output into a `csv` or `ods` format to edit tags in a spreadsheet, add a function to fetch that data and tag any changes
        - Because manually making changes into the json file also requires certain characters to be escaped properly (`\uxxxx`)
      - first one would be cool, but it assumes you have a tag editor \(insert shoutout to [Puddletag](https://github.com/puddletag/puddletag) here\), i'd much rather have a csv to modify them since it's a lot easier and more accessible

- [x] Log unavailable videos into a file.
  - [ ] Could be better

- [ ] Exit and notify the user somehow when `yt-dlp` outputs `Sign in to confirm you’re not a bot. This helps protect our community.`
  - [x] Break download loop
  - [ ] Use an alternative?
    - Piped
    - [Invidious](https://github.com/grqz/yt-dlp-invidious)

- [ ] Break when there is no internet connection in download loop
  - ERROR: [youtube] Fj7SH-YfH6A: Failed to extract any player response; please report this issue on  <https://github.com/yt-dlp/yt-dlp/issues?q=> , filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U

## III Requires Research

- [ ] Find out if there is a better way to structure the CLI logic or make it more maintainable in general [click](https://click.palletsprojects.com/en/8.1.x/)?

- [ ] Do async downloading

- [ ] Find out if this output from `yt-dlp` affects anything `WARNING: [youtube] Failed to download m3u8 information: HTTP Error 429: Too Many Requests`

- [ ] Fetch lyrics and add them into `library.json`
  - Sources that RiMusic is using seems pretty solid.

- [ ] Write tests

- [ ] InnerTube

## IV Lowest Importance

- [ ] Log bad thumbnails
  - [ ] `hqdefault`
  - [ ] Ones that are available as `hqdefault` but aren't a square (`720x720`)

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

- [ ] Give some use to CSV <-> JSON conversion functions

- [ ] Fetch metadata from YouTube instead of using the existing data

- [ ] remove exceptions/cases/if statements that shouldn't naturally occur

- [ ] Store `debug_print` printouts from each session

- [x] Improve debug prints,
  - [ ] Change errors that are handled to warnings or something else

- [ ] Implement `yt-dlp --get-filename -o "%(uploader)s hsfOqb5r8m0VbV31 %(title)s" VIDEO_URL` for null artists, which is caused by ViMusic's search function returning empty

- [ ] Write `PermissionError` exceptions

- [ ] Some languages have characters that are indexed inside the latin alphabet and by default I think Python just looks for its unicode index, so fixing this

- [ ] Rename `linuxpkgRequirements.sh` to `wingetRequirements.sh` and use the available package manager to install the packages.
  - `pacman(Arch) -S`, `dnf(Red Hat/Fedora) install`, `apt(Debian/Ubuntu) install`, `zypper(SLES/openSUSE) install`, `emerge(Gentoo)`

## V Doubts and Head Scratchers

- [ ] Find something that doesn't disrupt the user's workflow while getting the `likesPage`
  - cookie injection with selenium?
  - undetected chromedriver?
  - user script?

- RiMusic database adds all artists text whereas parser just gets the first one
  - look into artists text and separate the text if it has a comma or an ampersand
    - while this is pretty easy to do it might produce false artist names
  - see if `yt-dlp` can provide any information about this
  - leave it, the parsed data will never be perfect and require some manual changes for it to be pristine anyway

## VI TK Gui Deprecation

Current TK GUI will be replaced with something like ImGui.

## Latest Implementations & Fixes

NOTE: These will be removed after a while.

- [x] Make the entire project an executable that is usable with command line input with defaults if parameters aren't changed
  - [x] PyInstaller

- [x] Ignore user config, copy the `defaultConfig.yaml` if there isn't a config file yet.

- [x] Write intermediate functions, i.e functions that are chained together in `tkgui.py` right now to use them both in CLI&GUI
