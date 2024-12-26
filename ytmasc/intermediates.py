from json import dump
from logging import getLogger
from os import listdir, path, remove
from re import match
from shutil import rmtree

from eyed3 import load as loadmp3
from pandas import read_csv

from ytmasc.converter import convert_bulk
from ytmasc.downloader import download_bulk
from ytmasc.tagger import tag_bulk
from ytmasc.utility import (
    audio_conversion_ext,
    current_path,
    data_path,
    download_path,
    library_data,
    library_data_path,
    library_page,
    library_page_path,
    read_json,
    sort_dictionary_based_on_value_inside_nested_dictionary,
    update_yaml,
    write_json,
    yaml_config,
)

logger = getLogger(__name__)


def delete_library_page_files(fetcher_is_going_to_run: bool):
    try:
        remove(library_page_path)
        rmtree(f"{library_page_path[:-4]}_files")
        logger.info(
            f"Successfully deleted {library_page} and {library_page_path[:-4]}_files."
        )

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

    for filename in listdir(path.join(current_path, data_path)):
        matched = match(pattern, filename)
        if matched is not None and matched.group(1) is not None:  # what
            number = int(matched.group(1))
            if number > newest_number:
                newest_number = number
                newest_file = path.join(current_path, data_path, filename)

    return newest_file


def update_library_with_manual_changes_on_files():
    existing_data = read_json(library_data_path)
    modified_data = existing_data

    for watch_id, value in existing_data.items():
        song = loadmp3(path.join(download_path, watch_id + audio_conversion_ext))
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

    json = sort_dictionary_based_on_value_inside_nested_dictionary(modified_data)
    write_json(library_data_path, json)


def run_tasks(download: bool, convert: bool, tag: bool):
    if not check_if_data_exists("library") or not path.getsize(library_data_path) > 0:
        logger.error(
            f"[FileNotFoundError] {library_data} doesn't exist or is empty. Build {library_data} by running a parse or importing data."
        )
        pass

    else:
        json = read_json(library_data_path)
        if download:
            download_bulk(json)

        if convert:
            convert_bulk(json)

        if tag:
            tag_bulk(json)


def check_if_data_exists(source: str) -> bool:
    if source == "library":
        return True if path.isfile(library_data_path) else False
    if source == "export_ri":
        return True if find_newest_ri_music_export() else False


def create_config():
    if not path.exists(yaml_config):
        logger.info("Config doesn't exist, creating..")
        default_config = {
            "fetcher": {
                "closing-delay": 3,  # 5,
                "dialog-wait-delay": 0.5,  # 3
                "inbetween-delay": 0.2,  # 2
                "opening-delay": 6,  # 4
                "resend-amount": 60,  # 1
                "save-page-as-index-on-right-click": 5,  # 6
            },
            "parser": {
                "delete-library-page-files-afterwards": 0,
                "parse-library-page": 0,
                "parse-ri-music-db": 0,
                "run-fetcher": 0,
            },
            "tasks": {
                "convert": 0,
                "download": 0,
                "tag": 0,
            },
        }
        update_yaml(yaml_config, default_config)


def import_csv(csv_file: str, overwrite=True):
    df = read_csv(csv_file)
    df.fillna("", inplace=True)
    json_data = read_json(library_data_path)

    for index, row in df.iterrows():
        watch_id = row.iloc[0]
        artist = row.iloc[1]
        title = row.iloc[2]

        json_data = update_library_for_watch_id(
            json_data, watch_id, artist, title, overwrite
        )

    write_json(library_data_path, json_data)


def update_library_for_watch_id(json_data, watch_id, artist, title, overwrite):
    if watch_id in json_data:
        logger.info(f"Watch ID {watch_id} is already in the library.")
        if (
            (json_data[watch_id]["artist"] != artist)
            or (json_data[watch_id]["title"] != title)
        ) and overwrite:
            logger.info(
                f"Values don't match, updating with:\n"
                f"\tartist: {json_data[watch_id]['artist']} -> {artist}\n"
                f"\ttitle: {json_data[watch_id]['title']} -> {title}"
            )
            json_data[watch_id] = {"artist": artist, "title": title}

        elif (json_data[watch_id]["artist"] == "") or (
            json_data[watch_id]["title"] == ""
        ):
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
