import logging
import os
import shutil
import sqlite3

import eyed3
import pandas

from ytmasc.tasks import Tasks
from ytmasc.utility import (
    audio_conversion_ext,
    download_path,
    get_file_extension,
    get_filename,
    library_data,
    library_data_path,
    library_page,
    library_page_path,
    read_json,
    sort_nested,
    write_json,
)

logger = logging.getLogger(__name__)


def delete_library_page_files(fetcher_is_going_to_run: bool):
    try:
        os.remove(library_page_path)
        shutil.rmtree(f"{get_filename(library_page_path)}_files")

    except FileNotFoundError:
        if fetcher_is_going_to_run:
            pass

        else:
            pass


def update_library_with_manual_changes_on_files():
    existing_data = read_json(library_data_path)
    modified_data = existing_data

    for watch_id, value in existing_data.items():
        song = eyed3.load(os.path.join(download_path, watch_id + audio_conversion_ext))
        if not (value["title"] == song.tag.title or value["artist"] == song.tag.artist):
            modified_data[watch_id] = {
                "artist": song.tag.artist,
                "title": song.tag.title,
            }

    json = sort_nested(modified_data)
    write_json(library_data_path, json)


def run_tasks(download: bool, convert: bool, tag: bool):
    if not os.path.exists(library_data_path) or not os.path.getsize(library_data_path) > 0:
        pass

    else:
        json = read_json(library_data_path)
        if download:
            Tasks.download_bulk(json)

        if convert:
            Tasks.convert_bulk(json)

        if tag:
            Tasks.tag_bulk(json)


def import_path(file: str, overwrite=False):
    ext = get_file_extension(file)

    if os.path.isfile(file):
        if ext == "csv":
            df = pandas.read_csv(file)
            df.fillna("", inplace=True)
            json_data = read_json(library_data_path)

            for index, row in df.iterrows():
                watch_id = row.iloc[0]
                artist = row.iloc[1]
                title = row.iloc[2]

                json_data = update_library_for_watch_id(json_data, watch_id, artist, title, overwrite)

            write_json(library_data_path, json_data)

        elif ext == ".db":
            connection = sqlite3.connect(file)
            cursor = connection.cursor()

            cursor.execute("SELECT id, title, artistsText, likedAt FROM Song WHERE likedAt IS NOT NULL")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()

            json_data = read_json(library_data_path)

            for row in rows:
                watch_id, title, artist, liked_at = row

                json_data = update_library_for_watch_id(json_data, watch_id, artist, title, overwrite)

            write_json(library_data_path, json_data)

        else:
            pass
    else:
        pass


def update_library_for_watch_id(json_data, watch_id, artist, title, overwrite):
    if watch_id in json_data:
        if ((json_data[watch_id]["artist"] != artist) or (json_data[watch_id]["title"] != title)) and overwrite:
            json_data[watch_id] = {"artist": artist, "title": title}

        elif (json_data[watch_id]["artist"] == "") or (json_data[watch_id]["title"] == ""):
            json_data[watch_id] = {"artist": artist, "title": title}
    else:
        json_data[watch_id] = {"artist": artist, "title": title}

    return sort_nested(json_data)
