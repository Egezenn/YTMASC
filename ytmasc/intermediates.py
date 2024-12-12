"Provides chained functions for UX."
from inspect import currentframe
from os import listdir, path, remove
from re import match
from shutil import rmtree

from eyed3 import load as loadmp3

from .converter import convert_bulk
from .downloader import download_bulk
from .tagger import tag_bulk
from .utility import (
    audio_conversion_ext,
    current_path,
    data_path,
    debug_print,
    download_path,
    get_current_file,
    get_current_function,
    library_data,
    library_data_path,
    library_page,
    library_page_path,
    read_json,
    sort_dictionary_based_on_value_inside_nested_dictionary,
    write_json,
)

current_file = get_current_file(__file__)


def delete_library_page_files(fetcher_is_going_to_run: bool):
    current_function = get_current_function(currentframe())

    try:
        remove(library_page_path)
        rmtree(f"{library_page_path[:-4]}_files")
        debug_print(
            current_file,
            current_function,
            "i",
            f"Successfully deleted {library_page} and {library_page_path[:-4]}_files.",
        )

    except FileNotFoundError:
        if fetcher_is_going_to_run:
            pass

        else:
            debug_print(
                current_file,
                current_function,
                "e",
                "File(s) do not exist!",
                error_type="FileNotFoundError",
            )
            pass

    except PermissionError:
        debug_print(
            current_file,
            current_function,
            "e",
            "File(s) are in use!",
            error_type="PermissionError",
        )
        # TODO wait a little then retry?
        pass


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
    current_function = get_current_function(currentframe())

    existing_data = read_json(library_data_path)

    for key, value in existing_data.items():
        song = loadmp3(path.join(download_path, key + audio_conversion_ext))
        if not (
            value["title"] == song.tag.title and value["artist"] == song.tag.artist
        ):
            debug_print(
                current_file,
                current_function,
                "i",
                f"Manual change detected on {key}, updating {library_data} with changes:\n"
                f"artist:\t{song.tag.artist} -> {value['artist']}\n"
                f"title:\t{song.tag.title} -> {value['title']}\n",
            )
            song.tag.artist = value["artist"]
            song.tag.title = value["title"]
            song.tag.save()

    json = sort_dictionary_based_on_value_inside_nested_dictionary(existing_data)
    write_json(library_data_path, json)


def run_tasks(download: bool, convert: bool, tag: bool):
    current_function = get_current_function(currentframe())

    if not path.exists(library_data_path) or not path.getsize(library_data_path) > 0:
        debug_print(
            current_file,
            current_function,
            "e",
            f"{library_data} doesn't exist or is empty. Build {library_data} by running a parse.",
            error_type="FileNotFoundError",
        )

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
