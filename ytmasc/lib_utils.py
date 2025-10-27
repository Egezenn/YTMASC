import logging
import os

import mutagen.easyid3
import prettytable
import ytmusicapi

from ytmasc.utility import audio_conversion_ext, get_filename

# refactor to not use these
old_music_library = r"old"
new_music_library = r"downloads"
files_to_keep = r"!keep"
files_to_remove = r"!remove"

logger = logging.getLogger(__name__)


class ComparisonUtilities:
    # TODO check function get_filename

    @staticmethod
    def list_mp3(dir: str) -> list[list[dict], int]:
        filtered = [
            f for f in os.listdir(dir) if (f.endswith(audio_conversion_ext[0]) or f.endswith(audio_conversion_ext[1]))
        ]

        return filtered

    # will fail without the fallback
    @staticmethod
    def create_old_database(title_filename_fallback=False):
        old_files = ComparisonUtilities.list_mp3(old_music_library)
        old_database = []
        for old_song in old_files:
            data = mutagen.easyid3.EasyID3(os.path.join(old_music_library, old_song))
            if title_filename_fallback:
                title = get_filename(old_song)  # make a switch based on an user input
            else:
                title = data.get("Title")[0]
            artist = data.get("Artist")[0]
            old_database.append({get_filename(old_song): {"artist": artist, "title": title}})

        old_file_amt = 0
        for _ in old_files:
            old_file_amt += 1

        return old_database, old_file_amt

    @staticmethod
    def create_new_database() -> list[dict]:
        new_files = ComparisonUtilities.list_mp3(new_music_library)
        new_database = []
        for new_song in new_files:
            data = mutagen.easyid3.EasyID3(os.path.join(new_music_library, new_song))
            title = data.get("Title")[0]
            if data.get("Artist") is not None:
                artist = data.get("Artist")[0]
            else:
                artist = "░"  # so that there's no unpacking errors or something xd
            new_database.append({get_filename(new_song): {"artist": artist, "title": title}})

        return new_database

    @staticmethod
    def sort_based_on_score(scores, by_which) -> list:
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

    @staticmethod
    def init_table() -> classmethod:
        table = prettytable.PrettyTable()
        table.border = False
        table.hrules = False
        table.field_names = [
            "\x1b[100m\x1b[1m  TITLE SCORE  \x1b[0m",
            "\x1b[100m\x1b[1m  ARTIST SCORE  \x1b[0m",
            "\x1b[100m\x1b[1m  TITLE  \x1b[0m",
            "\x1b[100m\x1b[1m  ARTIST  \x1b[0m",
        ]

        return table

    @staticmethod
    def insert_rows(data, table, amount_to_insert=8, truncate_at=40):
        for i, item in enumerate(data):
            if i == amount_to_insert:
                break
            display_title_score = str(next(iter(item)))
            display_artist_score = str(list(item.values())[0]["ツ"])
            display_title = list(item.values())[0]["title"]
            display_title = display_title[:truncate_at] + "..." if len(display_title) > truncate_at else display_title
            display_artist = list(item.values())[0]["artist"]
            display_artist = (
                display_artist[:truncate_at] + "..." if len(display_artist) > truncate_at else display_artist
            )
            table.add_row(
                [
                    "\x1b[91m" + display_title_score + "\x1b[0m",
                    "\x1b[92m" + display_artist_score + "\x1b[0m",
                    "\x1b[93m" + display_title + "\x1b[0m",
                    "\x1b[94m" + display_artist + "\x1b[0m",
                ]
            )

    @staticmethod
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


class FailReplacementUtilities:
    @staticmethod
    def init_table() -> classmethod:
        table = prettytable.PrettyTable()
        table.border = False
        table.hrules = False
        table.field_names = [
            "\x1b[100m\x1b[1m  ARTIST(S)  \x1b[0m",
            "\x1b[100m\x1b[1m  WATCH ID  \x1b[0m",
            "\x1b[100m\x1b[1m  TITLE  \x1b[0m",
            "\x1b[100m\x1b[1m  ALBUM  \x1b[0m",
        ]

        return table

    @staticmethod
    def insert_data(self, table: classmethod, artist: str, watch_id: str, title: str, album: str):
        table.add_row(
            [
                f"\x1b[101m\x1b[1m  {artist}  \x1b[0m",
                f"\x1b[102m\x1b[1m  {watch_id}  \x1b[0m",
                f"\x1b[103m\x1b[1m  {title}  \x1b[0m",
                f"\x1b[104m\x1b[1m  {album}  \x1b[0m",
            ]
        )


def remove_duplicates_by_second_item(list_of_lists: list) -> list:
    seen = set()
    result = []

    for sublist in list_of_lists:
        if len(sublist) > 1:
            second_item = sublist[1]
            if second_item not in seen:
                seen.add(second_item)
                result.append(sublist)

    return result


def get_metadata_from_query(query: str) -> list:
    """Get songs metadata from the provided query. e.g Linkin Park - Numb
    First one is the most popular video as a fallback. (for some reason the artist for it returns as watch count)
    """

    yt = ytmusicapi.YTMusic()
    search_results = yt.search(query, ignore_spelling=True)

    results_metadata = []
    for result in search_results:
        if result["category"] not in [
            "More from YouTube",
            "Videos",
            "Community playlists",
            "Featured playlists",
            "Artists",
            "Podcasts",
            "Profiles",
            "Episodes",
            "Albums",
        ]:
            artists = []
            for artist in result["artists"]:
                artists.append(artist["name"])
            watch_id = result["videoId"]
            title = result["title"]
            try:
                album = result["album"]["name"]
            except:
                album = None

        results_metadata.append([artists, watch_id, title, album])
    results_metadata = remove_duplicates_by_second_item(results_metadata)

    return results_metadata


def get_metadata_from_watch_id(watch_id: str) -> list[str, str]:
    yt = ytmusicapi.YTMusic()

    search_results = yt.get_song(watch_id)

    artist = search_results["videoDetails"]["author"]
    # does this provide a list if there's more than one?
    title = search_results["videoDetails"]["title"]

    return artist, title
