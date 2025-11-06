"Rough tooling, mostly written for my migration case. Needs an overhaul."

from difflib import SequenceMatcher
import logging
import os
import re
import sys
import time

import keyboard
import mutagen
import requests.exceptions

import lib_utils
import utility

logger = logging.getLogger(__name__)


def compare():
    if not os.path.isdir(lib_utils.old_music_library):
        os.mkdir(lib_utils.old_music_library)
        sys.exit()

    for directory in [
        lib_utils.new_music_library,
        lib_utils.files_to_keep,
        lib_utils.files_to_remove,
    ]:
        if not os.path.isdir(directory):
            os.mkdir(directory)

    # database to be replaced
    old_database, old_file_amt = lib_utils.ComparisonUtilities.create_old_database()

    # ytmasc database
    new_database = lib_utils.ComparisonUtilities.create_new_database()

    # comparisons
    os.system("clear")
    for i, data_old in enumerate(old_database, start=1):
        scores = []
        old_title = data_old[next(iter(data_old))]["title"]
        old_artist = data_old[next(iter(data_old))]["artist"]

        for data_new in new_database:
            new_title = data_new[next(iter(data_new))]["title"]
            new_artist = data_new[next(iter(data_new))]["artist"]
            title_score = int(SequenceMatcher(None, old_title.lower(), new_title.lower()).ratio() * 100)
            artist_score = int(SequenceMatcher(None, old_artist.lower(), new_artist.lower()).ratio() * 100)
            scores.append(
                {
                    title_score: {
                        "ツ": artist_score,
                        "title": new_title,
                        "artist": new_artist,
                    }
                }
            )

        file = os.pathjoin(lib_utils.old_music_library, f"{next(iter(data_old))}.mp3")
        sorted_data_title = lib_utils.ComparisonUtilities.sort_based_on_score(scores, "title_score")
        sorted_data_artist = lib_utils.ComparisonUtilities.sort_based_on_score(scores, "artist_score")

        # skip 100 & 100 matches
        if (
            next(iter(sorted_data_title[0])) == 100
            and sorted_data_title[0][next(iter(sorted_data_title[0]))]["ツ"] == 100
        ):
            os.system("clear")
            print(f"{utility.zfill_progress(i, old_file_amt)}\nremove: {file}\n")
            os.rename(
                file,
                os.pathjoin(lib_utils.files_to_remove, f"{next(iter(data_old))}.mp3"),
            )

        # user decisions
        else:
            print(f"r=remove, k=keep, i=ignore\n")
            table = lib_utils.ComparisonUtilities.init_table()
            lib_utils.ComparisonUtilities.insert_old_file_data(table, old_title, old_artist, column_to_mark=1)
            lib_utils.ComparisonUtilities.insert_rows(sorted_data_title, table, truncate_at=30)
            lib_utils.ComparisonUtilities.insert_old_file_data(table, old_title, old_artist, column_to_mark=2)
            lib_utils.ComparisonUtilities.insert_rows(sorted_data_artist, table, truncate_at=30)
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
                    print(f"{utility.zfill_progress(i, old_file_amt)}\nremove: {file}\n")
                    os.rename(
                        file,
                        os.pathjoin(
                            lib_utils.files_to_remove,
                            f"{next(iter(data_old))}.mp3",
                        ),
                    )
                elif input_key == "k":
                    os.system("clear")
                    print(f"{utility.zfill_progress(i, old_file_amt)}/{old_file_amt}\nkeep: {file}\n")
                    os.rename(
                        file,
                        os.pathjoin(
                            lib_utils.files_to_keep,
                            f"{next(iter(data_old))}.mp3",
                        ),
                    )
                elif input_key == "i":
                    os.system("clear")
                    print(f"{utility.zfill_progress(i, old_file_amt)}/{old_file_amt}\nignore: {file}\n")
                else:
                    sys.exit()
                    # keyboard doesn't care about terminal focus and i don't know which package would do handle that easily
                    # so, don't multi task? yet?
                # wait for key up


def find_same_metadata():
    # TODO add functionality to remove either one, create a blacklist and add that to it
    data = lib_utils.ComparisonUtilities.create_new_database()

    for watch_id in data:
        for watch_id2 in data:
            if watch_id != watch_id2:
                artist_score = int(
                    SequenceMatcher(
                        None,
                        watch_id[next(iter(watch_id))]["artist"],
                        watch_id2[next(iter(watch_id2))]["artist"],
                    ).ratio()
                    * 100
                )
                title_score = int(
                    SequenceMatcher(
                        None,
                        watch_id[next(iter(watch_id))]["title"],
                        watch_id2[next(iter(watch_id2))]["title"],
                    ).ratio()
                    * 100
                )
                if artist_score == 100 and title_score == 100:
                    print(f"{next(iter(watch_id))} and {next(iter(watch_id2))} are same.")


def find_unpaired(delete=None):
    files = os.listdir(utility.download_path)

    audio_files = [
        f for f in files if f.endswith(utility.audio_conversion_ext[0]) or f.endswith(utility.audio_conversion_ext[1])
    ]
    image_files = [f for f in files if f.endswith(utility.source_cover_ext)]

    audio_base = []
    for audio in audio_files:
        audio_base.append(utility.get_filename(audio))
    image_base = []
    for image in image_files:
        image_base.append(utility.get_filename(image))

    unpaired_audio = [s for s in audio_files if all(sub not in s for sub in image_base)]
    unpaired_image = [s for s in image_base if all(sub not in s for sub in audio_base)]

    if delete == "audio":
        for audio in unpaired_audio:
            for ext in utility.audio_conversion_ext:
                if os.path.isfile(audio + ext):
                    os.remove(os.path.join(utility.download_path, audio + ext))
                    break
    if delete == "image":
        for image in unpaired_image:
            os.remove(os.path.join(utility.download_path, image + utility.source_cover_ext))

    print("Unpaired audio files:", *unpaired_audio, "\n\nUnpaired image files:", *unpaired_image)


def replace_fails():
    # TODO add functionality to replace the watch id on the library with the users choice, blacklist the bad one
    lines = utility.read_txt_as_list(utility.fail_log_path)
    for line in lines:
        watch_id = re.search(r"\[youtube\] ([a-zA-Z0-9\-_]*?):", line).group(1)
        artist, title = lib_utils.get_metadata_from_watch_id(watch_id)
        os.system("clear")
        query = f"{artist} - {title}"
        print(query)
        results = lib_utils.get_metadata_from_query(query)
        table = lib_utils.FailReplacementUtilities.init_table()
        for result in results:
            lib_utils.FailReplacementUtilities.insert_data(table, *result)
        print(table)
        input_key = ""
        while input_key not in ["esc"]:
            input_key = keyboard.read_key()


def refetch_metadata(skip_until=-1, force=False):
    # TODO do the skip amount properly, theres some offset to it, too lazy to debug it
    json_data = utility.read_json(utility.library_data_path)
    for i, watch_id in enumerate(json_data, start=1):
        if i + 1 <= skip_until:
            continue
        try:
            if not force and not (json_data[watch_id]["artist"] and json_data[watch_id]["title"]):
                artist, title = lib_utils.get_metadata_from_watch_id(watch_id)
                logger.info(f"\n{watch_id} is empty, pulled data:\n{artist} - {title}")
                json_data = utility.update_library_for_watch_id(json_data, watch_id, artist, title, overwrite=True)
            elif force:
                artist, title = lib_utils.get_metadata_from_watch_id(watch_id)
                logger.info(f"\nForcefully repulled data for {watch_id}:\n{artist} - {title}")
                json_data = utility.update_library_for_watch_id(json_data, watch_id, artist, title, overwrite=True)
            else:
                logger.info(f"\nSkipped fetch for {watch_id}")

            if not i % 10:
                logger.debug(f"Saved")
                utility.write_json(utility.library_data_path, json_data)
        except requests.exceptions.ConnectionError:
            logger.info(f"Couldn't fetch metadata for {watch_id}!")
            break

    utility.write_json(utility.library_data_path, json_data)


def generate_playlist(file_dir):
    with open(file_dir + ".m3u", "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")
        for file in sorted(os.listdir(utility.download_path)):
            for ext in [*utility.source_audio_ext, *utility.audio_conversion_ext]:
                if file.endswith(ext):
                    path = os.path.join(utility.current_path, utility.download_path, file)
                    audio = mutagen.File(path, easy=True)
                    artist = audio.get("artist", [""])[0]
                    title = audio.get("title", [""])[0]
                    if artist and title:
                        m3u.write(f"#EXTINF:-1,{artist} - {title}\n" + path + "\n")
                    else:
                        m3u.write(path + "\n")
                    break
