# YTMASC

<a href="#"><img alt="horrible orange triangle" style="padding:16px;" align="left" src="assets/icon.svg"></a>

YTMASC(**Y**ou**T**ube **M**usic **A**udio **S**craper & syn**C**hronizer) in a nutshell, aims to get your music library off of YouTube and provide you an offline backup of it along with other maintenance niceties.

Grab the latest alpha version [here](https://github.com/Egezenn/YTMASC/releases)!

It's features are:

- Scraping your library page from YouTube
- Importing favorites from a [RiMusic](https://github.com/fast4x/RiMusic) database
- Import a CSV of your own (columns are: `ID`, `artist`, `title`)
- Maintaining a data file for your music for an easily reproducible collection
- Automatic downloading, converting and tagging
- Some helper functions to modify your data file easier and for easy migration
- A GUI and a CLI (shipped as a binary for Windows!)

The project just keeps expanding as I learn more stuff and want to implement niche things. So it's currently in Alpha stages, you may see new features come and go every now and then.

## CLI Usage Examples

`ytmasc` | `ytmasc gui`: launches the deprecated gui

`ytmasc -h`: shows the help

`ytmasc gui`: will run the tkinter gui (it may get broken in the future)

`ytmasc run`: runs tasks according to the current configuration

`ytmasc set`: will show you the state of the config

`ytmasc set parser run_fetcher 1`: sets the fetcher to run

`ytmasc --export_library_as_csv`: exports the library as csv to the `data` directory

## Requirements to run from source or build

- You need `~=python3.11` (also `python3-tk` for the GUI on Linux) and `ffmpeg` packages.

## Side notes

- You need `ffmpeg` binaries for conversion.
- YouTube blocks API requests if you exceed the amount they classify you as a bot (around 200 requests). You can either use a VPN, proxy or just wait to bypass this. See related `yt-dlp` [issue](https://github.com/yt-dlp/yt-dlp/issues/10128).
- You might want to change your YouTube language while the fetcher is running as YouTube has rare concatenation of artists which gives you the word "and" in your own language.
- While downloading, some changes may occur in YouTube which results in an error.
Find out the music via `https://music.youtube.com/watch?v=<key>`, delete the json entry and add the changed one into your likes to continue. At least your music is not lost by YouTube for some unknown reason! :\)

### `fetcher.py`

This part is a little duct taped, I couldn't find a good way to get the `libraryPage` formerly known as `likesPage` so I just emulated user input. It's written for a Windows computer that has `firefox` and `file explorer`. Shouldn't be hard to tinker and get it to work for your configuration.

Change `resendAmount` based on your internet connection, page length. For reference with good connection and 600~ likes containing page requires about 60.

Change `openingDelay` based on your internet connection.

Change `savePageAsIndexOnRightClick` to which index your save as is on your browser.

The rest is fine if you don't have a really old computer.

## Credits

I'd like to personally thank all the people that have developed\/maintained\/poured their hearts into the packages\/tools this *thing* is using and the artists that pushed me to keep a copy of their music in my library.

## Disclaimer

This project is not in any way, shape or form affiliated with YouTube, Google or any of their subsidiaries and affiliates.
