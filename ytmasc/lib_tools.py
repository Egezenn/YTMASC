import logging
import os
import re
import time

import fuzzywuzzy
import keyboard

from ytmasc.intermediates import update_library_for_watch_id
from ytmasc.lib_utils import (
    ComparisonUtilities,
    FailReplacementUtilities,
    files_to_keep,
    files_to_remove,
    get_metadata_from_query,
    get_metadata_from_watch_id,
    new_music_library,
    old_music_library,
)
from ytmasc.utility import (
    count_key_amount_in_json,
    download_path,
    fail_log_path,
    get_file_extension,
    library_data_path,
    read_json,
    read_txt_as_list,
    write_json,
    zfill_progress,
)

logger = logging.getLogger(__name__)


def compare():
    if not os.path.isdir(old_music_library):
        os.mkdir(old_music_library)
        exit()

    for directory in [
        new_music_library,
        files_to_keep,
        files_to_remove,
    ]:
        if not os.path.isdir(directory):
            os.mkdir(directory)

    # database to be replaced
    old_database, old_file_amt = ComparisonUtilities.create_old_database()

    # ytmasc database
    new_database = ComparisonUtilities.create_new_database()

    # comparisons
    os.system("clear")
    for i, data_old in enumerate(old_database, start=1):
        scores = []
        old_title = data_old[next(iter(data_old))]["title"]
        old_artist = data_old[next(iter(data_old))]["artist"]

        for data_new in new_database:
            new_title = data_new[next(iter(data_new))]["title"]
            new_artist = data_new[next(iter(data_new))]["artist"]
            title_score = fuzzywuzzy.fuzz.ratio(old_title.lower(), new_title.lower())
            artist_score = fuzzywuzzy.fuzz.ratio(old_artist.lower(), new_artist.lower())
            scores.append(
                {
                    title_score: {
                        "ツ": artist_score,
                        "title": new_title,
                        "artist": new_artist,
                    }
                }
            )

        file = os.pathjoin(old_music_library, f"{next(iter(data_old))}.mp3")
        sorted_data_title = ComparisonUtilities.sort_based_on_score(scores, "title_score")
        sorted_data_artist = ComparisonUtilities.sort_based_on_score(scores, "artist_score")

        # skip 100 & 100 matches
        if (
            next(iter(sorted_data_title[0])) == 100
            and sorted_data_title[0][next(iter(sorted_data_title[0]))]["ツ"] == 100
        ):
            os.system("clear")
            print(f"{zfill_progress(i, old_file_amt)}\nremove: {file}\n")
            os.rename(
                file,
                os.pathjoin(files_to_remove, f"{next(iter(data_old))}.mp3"),
            )

        # user decisions
        else:
            print(f"r=remove, k=keep, i=ignore\n")
            table = ComparisonUtilities.init_table()
            ComparisonUtilities.insert_old_file_data(table, old_title, old_artist, column_to_mark=1)
            ComparisonUtilities.insert_rows(sorted_data_title, table, truncate_at=30)
            ComparisonUtilities.insert_old_file_data(table, old_title, old_artist, column_to_mark=2)
            ComparisonUtilities.insert_rows(sorted_data_artist, table, truncate_at=30)
            print(table)

            input_key = ""
            while input_key not in ["r", "k", "i"]:
                input_key = keyboard.read_key()
                time.sleep(0.5)  # temp solution before wait for key up
                # if input_key not in ["r", "k", "i"]:
                #     input_key = ""
                #     system("clear")
                #     print("press h to continue..")
                #     while input_key != "h":
                #         input_key = read_key()
                #         time.sleep(0.5)
                if input_key == "r":
                    os.system("clear")
                    print(f"{zfill_progress(i, old_file_amt)}\nremove: {file}\n")
                    os.rename(
                        file,
                        os.pathjoin(
                            files_to_remove,
                            f"{next(iter(data_old))}.mp3",
                        ),
                    )
                elif input_key == "k":
                    os.system("clear")
                    print(f"{zfill_progress(i, old_file_amt)}/{old_file_amt}\nkeep: {file}\n")
                    os.rename(
                        file,
                        os.pathjoin(
                            files_to_keep,
                            f"{next(iter(data_old))}.mp3",
                        ),
                    )
                elif input_key == "i":
                    os.system("clear")
                    print(f"{zfill_progress(i, old_file_amt)}/{old_file_amt}\nignore: {file}\n")
                else:
                    quit()
                    # keyboard doesn't care about terminal focus and i don't know which package would do handle that easily
                    # so, don't multi task? yet?
                # wait for key up


def find_same_metadata():
    # TODO add functionality to remove either one, create a blacklist and add that to it
    data = ComparisonUtilities.create_new_database()

    for watch_id in data:
        for watch_id2 in data:
            if watch_id != watch_id2:
                artist_score = fuzzywuzzy.fuzz.ratio(
                    watch_id[next(iter(watch_id))]["artist"],
                    watch_id2[next(iter(watch_id2))]["artist"],
                )
                title_score = fuzzywuzzy.fuzz.ratio(
                    watch_id[next(iter(watch_id))]["title"],
                    watch_id2[next(iter(watch_id2))]["title"],
                )
                if artist_score == 100 and title_score == 100:
                    print(f"{next(iter(watch_id))} and {next(iter(watch_id2))} are same.")


def replace_fails():
    # TODO add functionality to replace the watch id on the library with the users choice, blacklist the bad one
    lines = read_txt_as_list(fail_log_path)
    for line in lines:
        watch_id = re.search(r"\[youtube\] ([a-zA-Z0-9\-_]*?):", line).group(1)
        artist, title = get_metadata_from_watch_id(watch_id)
        os.system("clear")
        query = f"{artist} - {title}"
        print(query)
        results = get_metadata_from_query(query)
        table = FailReplacementUtilities.init_table()
        for result in results:
            FailReplacementUtilities.insert_data(table, *result)
        print(table)
        input_key = ""
        while input_key not in ["esc"]:
            input_key = keyboard.read_key()


def replace_current_metadata_with_youtube(skip_until=-1):
    # TODO do the skip amount properly, theres some offset to it, too lazy to debug it
    json_data = read_json(library_data_path)
    total_operations = count_key_amount_in_json(library_data_path)
    for i, watch_id in enumerate(json_data, start=1):
        if i + 1 <= skip_until:
            continue
        try:
            artist, title = get_metadata_from_watch_id(watch_id)

            json_data = update_library_for_watch_id(json_data, watch_id, artist, title, overwrite=True)
        except:
            break

    write_json(library_data_path, json_data)


def find_unpaired_files():
    files = os.listdir(download_path)

    mp3_files = {get_file_extension(f) for f in files if f.endswith(".mp3")}
    jpg_files = {get_file_extension(f) for f in files if f.endswith(".jpg")}

    unpaired_mp3 = mp3_files - jpg_files
    unpaired_jpg = jpg_files - mp3_files

    print("Unpaired MP3 files:", *unpaired_mp3)
    print("Unpaired JPG files:", *unpaired_jpg)
