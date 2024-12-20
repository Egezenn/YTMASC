import os

from mutagen.easyid3 import EasyID3
from prettytable import PrettyTable

from ytmasc.utility import audio_conversion_ext

old_music_library = r"old"
new_music_library = r"downloads"
files_to_keep = r"!keep"
files_to_remove = r"!remove"


def list_mp3(dir: str) -> list:
    filtered = [f for f in os.listdir(dir) if f.endswith(audio_conversion_ext)]

    return filtered


def create_old_database(title_filename_fallback=False):
    old_files = list_mp3(old_music_library)
    old_database = []
    for OLD_song in old_files:
        data = EasyID3(os.path.join(old_music_library, OLD_song))
        if title_filename_fallback:
            title = OLD_song.split(".")[0]  # make a switch based on an user input
        else:
            title = data.get("Title")[0]
        artist = data.get("Artist")[0]
        old_database.append({title: artist})

    old_file_amt = 0
    for _ in old_files:
        old_file_amt += 1

    return old_database, old_file_amt


def create_new_database():
    new_files = list_mp3(new_music_library)
    new_database = []
    for NEW_song in new_files:
        data = EasyID3(os.path.join(new_music_library, NEW_song))
        title = data.get("Title")[0]
        if data.get("Artist") is not None:
            artist = data.get("Artist")[0]
        else:
            artist = "░"  # so that there's no unpacking errors or something xd
        new_database.append({title: artist})
    return new_database


def sort_based_on_score(scores, by_which):
    if by_which == "title_score":
        sorted_data = sorted(
            scores,
            key=lambda x: (int(next(iter(x))), x[next(iter(x))]["ツ"]),
            reverse=True,
        )
        return sorted_data
    elif by_which == "artist_score":
        sorted_data = sorted(
            scores,
            key=lambda x: (x[next(iter(x))]["ツ"], int(next(iter(x)))),
            reverse=True,
        )
        return sorted_data


def init_table():
    table = PrettyTable()
    table.border = False
    table.hrules = False
    table.field_names = [
        "\x1b[100m\x1b[1m  TiSC  \x1b[0m",
        "\x1b[100m\x1b[1m  ArSC  \x1b[0m",
        "\x1b[100m\x1b[1m  TITLE  \x1b[0m",
        "\x1b[100m\x1b[1m  ARTIST  \x1b[0m",
    ]


def insert_rows(data, table, amount_to_insert=8, truncate_at=40):
    for i, item in enumerate(data):
        if i == amount_to_insert:
            break
        display_title_score = str(next(iter(item)))
        display_artist_score = str(list(item.values())[0]["ツ"])
        display_title = list(item.values())[0]["title"]
        display_title = (
            display_title[:truncate_at] + "..."
            if len(display_title) > truncate_at
            else display_title
        )
        display_artist = list(item.values())[0]["artist"]
        display_artist = (
            display_artist[:truncate_at] + "..."
            if len(display_artist) > truncate_at
            else display_artist
        )
        table.add_row(
            [
                "\x1b[91m" + display_title_score + "\x1b[0m",
                "\x1b[92m" + display_artist_score + "\x1b[0m",
                "\x1b[93m" + display_title + "\x1b[0m",
                "\x1b[94m" + display_artist + "\x1b[0m",
            ]
        )


def insert_old_file_data(table, title, artist, column_to_mark=0):
    if column_to_mark == 1:
        table.add_row(
            [
                "\x1b[101m\x1b[1m  ^  \x1b[0m",
                "\x1b[102m\x1b[1m    \x1b[0m",
                f"\x1b[103m\x1b[1m {title} \x1b[0m",
                f"\x1b[104m\x1b[1m {artist} \x1b[0m",
            ]
        )
    elif column_to_mark == 2:
        table.add_row(
            [
                "\x1b[101m\x1b[1m    \x1b[0m",
                "\x1b[102m\x1b[1m  ^  \x1b[0m",
                f"\x1b[103m\x1b[1m {title} \x1b[0m",
                f"\x1b[104m\x1b[1m {artist} \x1b[0m",
            ]
        )
    else:
        table.add_row(
            [
                "\x1b[101m\x1b[1m    \x1b[0m",
                "\x1b[102m\x1b[1m    \x1b[0m",
                f"\x1b[103m\x1b[1m {title} \x1b[0m",
                f"\x1b[104m\x1b[1m {artist} \x1b[0m",
            ]
        )
