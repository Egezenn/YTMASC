# YTMASC

YTMASC(**Y**ou**T**ube **M**usic **A**udio **S**craper & syn**C**hronizer) in a nutshell, aims to get your music library off of YouTube and provide you an offline backup of it along with other maintenance niceties.

It's features are:

- Scraping your library page from YouTube
- Importing favorites from a [RiMusic](https://github.com/fast4x/RiMusic) database
- Maintaining a data file for your music for an easily reproducible collection
- Automatic downloading, converting and tagging
- Some helper functions to modify your data file easier and for easy migration
- A GUI and a CLI (shipped as a binary for Windows!)

The project just keeps expanding as I learn more stuff and want to implement niche things. So it's currently in Alpha stages, you may see new features come and go every now and then.

## I Requirements and notes

### I.A Windows

- You need `python3.11` and `ffmpeg` packages.
  - You can also run `msys2Requirements.sh` get these from MSYS2.
  - You can run `wingetRequirements.bat` if you have winget installed.
    - `ffmpeg` from wasn't working for me, just a heads up.

### I.B GNU/Linux

- You need `python3.11`, `ffmpeg` and `python3-tk` packages.
  - You can run `linuxpkgRequirements.sh` via the terminal.

### I.C Required python packages

- Run `pip install -r requirements.txt` command via the terminal.

### I.D Side notes

- YouTube blocks API requests if you exceed the amount they classify you as a bot (around 200 requests). You can either use a VPN, proxy or just wait to bypass this. See related `yt-dlp` [issue](https://github.com/yt-dlp/yt-dlp/issues/10128).
- You might want to change your YouTube language while the fetcher is running as YouTube has rare concatenation of artists which gives you the word "and" in your own language.
- While downloading, some changes may occur in YouTube which results in an error.
Find out the music via `https://music.youtube.com/watch?v=<key>`, delete the json entry and add the changed one into your likes to continue. At least your music is not lost by YouTube for some unknown reason! :\)

### I.E `fetcher.py`

This part is a little duct taped, I couldn't find a good way to get the `libraryPage` formerly known as `likesPage` so I just emulated user input. It's written for a Windows computer that has `firefox` and `file explorer`. Shouldn't be hard to tinker and get it to work for your configuration.

Change `resendAmount` based on your internet connection, page length. For reference with good connection and 600~ likes containing page requires about 60.

Change `openingDelay` based on your internet connection.

Change `savePageAsIndexOnRightClick` to which index your save as is on your browser.

The rest is fine if you don't have a really old computer.

## II CLI Usage Examples

`python -m ytmasc`

`-h`

`gui`: will run the tkinter gui (it may get broken in the future)

`run`: runs tasks according to the current configuration

`set`: will show you the state of the config

`set parser run_fetcher 1`: sets the fetcher to run

`--export_library_as_csv`: exports the library as csv to the `data` directory

## III Origin

Back in highschool I didn't have a data plan for my phone \(because I mostly used it to receive phone calls\), so I just downloaded songs and tagged them to listen on the way. From creating dumb scripts for games using AutoHotkey, I botched together some lines to semi-automize the stuff I do manually. It was horrendous. But managable with the size of my library at that time.

But as time passed, this library has expanded to 4 digits and so by being lazy and having a better programming knowledge I wanted to download my music library from YouTube *in a more convenient fashion*, but the existing tools can't do this. So, I started by parsing the library page on YouTube. Then formatting and outputting that into `yt-dl` to download the files. And realizing that I could do all this and other tedious maintenance with Python.

### But why would you still do all this work when you have easy ways to get the music you want?

Well, in the current era where companies became too restrictive of **how** you listen to your music and **enshittify** your experience in any way possible to justify their gains, this project is a callback to the serene days of maintaining your own library which is detached from any sort of service.

Music should not be paywalled. This era of short-form, disposable media demolished the sense of attachment to the artists. Music is part of our culture and it's our responsibility as an individual to shoutout what we like.

## IV Credits

I'd like to personally thank all the people that have developed\/maintained\/poured their hearts into the packages\/tools this *thing* is using and the artists that pushed me to keep a copy of their music in my library.

## V Disclaimer

This project is not in any way, shape or form affiliated with YouTube, Google or any of their subsidiaries and affiliates.
