"Provides chained functions for UX."
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

    highest_number = -1
    highest_file = None

    for filename in listdir(path.join(current_path, data_path)):
        matched = match(pattern, filename)
        if matched is not None and matched.group(1) is not None:  # what
            number = int(matched.group(1))
            if number > highest_number:
                highest_number = number
                highest_file = path.join(current_path, data_path, filename)
    return highest_file


def update_library_with_manual_changes_on_files():
    existing_data = read_json(library_data_path)
    modified_data = existing_data

    for key, value in existing_data.items():
        song = loadmp3(path.join(download_path, key + audio_conversion_ext))
        if not (value["title"] == song.tag.title or value["artist"] == song.tag.artist):
            logger.info(
                f"Manual change detected on {key}, updating {library_data} with changes:\n"
                f"artist:\t{song.tag.artist} -> {value['artist']}\n"
                f"title:\t{song.tag.title} -> {value['title']}\n",
            )
            modified_data[key] = {
                "artist": song.tag.artist,
                "title": song.tag.title,
            }

    json = sort_dictionary_based_on_value_inside_nested_dictionary(modified_data)
    write_json(library_data_path, json)


def run_tasks(download: bool, convert: bool, tag: bool):
    if not path.exists(library_data_path) or not path.getsize(library_data_path) > 0:
        logger.error(
            f"[FileNotFoundError] {library_data} doesn't exist or is empty. Build {library_data} by running a parse."
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


def check_if_data_exists():
    return (
        True
        if path.isfile(library_page_path)
        or find_newest_ri_music_export()
        or path.isfile(library_data_path)
        else False
    )


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


def import_csv(csv_file: str, json_file: str, overwrite=True):
    df = read_csv(csv_file)
    df.fillna("", inplace=True)
    json_data = read_json(json_file)

    for index, row in df.iterrows():
        key = row.iloc[0]
        value1 = row.iloc[1]
        value2 = row.iloc[2]

        if key in json_data:
            logger.info(f"Key {key} is already in the library.")
            if (
                (json_data[key]["artist"] != value1)
                or (json_data[key]["title"] != value2)
            ) and overwrite:
                logger.info(
                    f"Values don't match, updating with:\n"
                    f"artist: {json_data[key]['artist']} -> {row.iloc[1]}\n"
                    f"title: {json_data[key]['title']} -> {row.iloc[2]}"
                )
                json_data[key] = {"artist": value1, "title": value2}
        else:
            logger.info(
                f"Key {key} is not in library, adding it with values:\n"
                f"artist: {row.iloc[1]}\n"
                f"title: {row.iloc[2]}"
            )
            json_data[key] = {"artist": value1, "title": value2}

    with open(json_file, "w") as f:
        dump(json_data, f, indent=2)
