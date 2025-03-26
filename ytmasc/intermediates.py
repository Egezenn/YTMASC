import logging
import os
import re
import shutil

import eyed3
import pandas

from ytmasc.tasks import Tasks
from ytmasc.utility import (
    audio_conversion_ext,
    current_path,
    data_path,
    download_path,
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
        logger.info(f"Successfully deleted {library_page} and {get_filename(library_page_path)}_files.")

    except FileNotFoundError:
        if fetcher_is_going_to_run:
            pass

        else:
            logger.error("[FileNotFoundError] File(s) do not exist!")
            pass

    except PermissionError:
        logger.error("[PermissionError] File(s) are in use!")
        pass
        # TODO wait a little then retry?


def find_newest_ri_music_export():
    pattern = r"rimusic_(\d+)|vimusic_(\d+)"

    newest_number = -1
    newest_file = None

    for filename in os.listdir(os.path.join(current_path, data_path)):
        matched = re.match(pattern, filename)
        if matched is not None and matched.group(1) is not None:  # what
            number = int(matched.group(1))
            if number > newest_number:
                newest_number = number
                newest_file = os.path.join(current_path, data_path, filename)

    return newest_file


def update_library_with_manual_changes_on_files():
    existing_data = read_json(library_data_path)
    modified_data = existing_data

    for watch_id, value in existing_data.items():
        song = eyed3.load(os.path.join(download_path, watch_id + audio_conversion_ext))
        if not (value["title"] == song.tag.title or value["artist"] == song.tag.artist):
            logger.info(
                f"Manual change detected on {watch_id}, updating {library_data} with changes:\n"
                f"artist:\t{song.tag.artist} -> {value['artist']}\n"
                f"title:\t{song.tag.title} -> {value['title']}\n",
            )
            modified_data[watch_id] = {
                "artist": song.tag.artist,
                "title": song.tag.title,
            }

    json = sort_nested(modified_data)
    write_json(library_data_path, json)


def run_tasks(download: bool, convert: bool, tag: bool):
    if not check_if_data_exists("library") or not os.path.getsize(library_data_path) > 0:
        logger.error(
            f"[FileNotFoundError] {library_data} doesn't exist or is empty. Build {library_data} by running a parse or importing data."
        )
        pass

    else:
        json = read_json(library_data_path)
        if download:
            Tasks.download_bulk(json)

        if convert:
            Tasks.convert_bulk(json)

        if tag:
            Tasks.tag_bulk(json)


def check_if_data_exists(source: str) -> bool:
    if source == "library":
        return True if os.path.isfile(library_data_path) else False
    if source == "export_ri":
        return True if find_newest_ri_music_export() else False


def import_csv(csv_file: str, overwrite=True):
    df = pandas.read_csv(csv_file)
    df.fillna("", inplace=True)
    json_data = read_json(library_data_path)

    for index, row in df.iterrows():
        watch_id = row.iloc[0]
        artist = row.iloc[1]
        title = row.iloc[2]

        json_data = update_library_for_watch_id(json_data, watch_id, artist, title, overwrite)

    write_json(library_data_path, json_data)


def update_library_for_watch_id(json_data, watch_id, artist, title, overwrite):
    if watch_id in json_data:
        logger.info(f"Watch ID {watch_id} is already in the library.")
        if ((json_data[watch_id]["artist"] != artist) or (json_data[watch_id]["title"] != title)) and overwrite:
            logger.info(
                f"Values don't match, updating with:\n"
                f"\tartist: {json_data[watch_id]['artist']} -> {artist}\n"
                f"\ttitle: {json_data[watch_id]['title']} -> {title}"
            )
            json_data[watch_id] = {"artist": artist, "title": title}

        elif (json_data[watch_id]["artist"] == "") or (json_data[watch_id]["title"] == ""):
            logger.info(
                f"Overwrite not specified but artist and/or title metadata is empty:\n"
                f"\tartist: {json_data[watch_id]['artist']} -> {artist}\n"
                f"\ttitle: {json_data[watch_id]['title']} -> {title}"
            )
            json_data[watch_id] = {"artist": artist, "title": title}
    else:
        logger.info(
            f"Watch ID {watch_id} is not in json_data, adding it with values:\n"
            f"\tartist: {artist}\n"
            f"\ttitle: {title}"
        )
        json_data[watch_id] = {"artist": artist, "title": title}

    return json_data
