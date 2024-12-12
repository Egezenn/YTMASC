import os

from mutagen.easyid3 import EasyID3
from prettytable import PrettyTable

OLD_music_library = r"old"
NEW_music_library = r"new"  # or downloads
files_to_keep = r"!keep"
files_to_remove = r"!remove"


def create_old_database():
    OLD_FILES = os.listdir(OLD_music_library)
    OLD_DATABASE = []
    for OLD_song in OLD_FILES:
        data = EasyID3(os.path.join(OLD_music_library, OLD_song))
        title = OLD_song.split(".")[0]  # make a switch based on an user input
        # title = data.get("Title")[0]
        artist = data.get("Artist")[0]
        OLD_DATABASE.append({title: artist})

    old_file_amt = 0
    for file in OLD_FILES:
        old_file_amt += 1

    return OLD_DATABASE, old_file_amt


def create_new_database():
    NEW_FILES = os.listdir(NEW_music_library)
    NEW_DATABASE = []
    for NEW_song in NEW_FILES:
        data = EasyID3(os.path.join(NEW_music_library, NEW_song))
        title = data.get("Title")[0]
        if data.get("Artist") is not None:
            artist = data.get("Artist")[0]
        else:
            artist = "░"  # so that there's no unpacking errors or something xd
        NEW_DATABASE.append({title: artist})
    return NEW_DATABASE


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
