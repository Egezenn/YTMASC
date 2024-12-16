"Imports an old database and compares each file with new ones."
from os import path, mkdir, system, rename
from time import sleep
from inspect import currentframe

from fuzzywuzzy import fuzz
from keyboard import read_key

from ytmasc.dbtools.comparison_utils import (
    new_music_library,
    old_music_library,
    create_new_database,
    create_old_database,
    files_to_keep,
    files_to_remove,
    init_table,
    insert_old_file_data,
    insert_rows,
    sort_based_on_score,
)
from ytmasc.utility import debug_print, get_current_file, get_current_function

current_file = get_current_file(__file__)


def compare():
    """
    Compares each file in the old database with the ones that are downloaded
    with a CLI that handles keypresses.
    """

    if not path.isdir(old_music_library):
        current_function = get_current_function(currentframe())

        debug_print(
            current_file,
            current_function,
            "w",
            f"Directory `{old_music_library}` doesn't exist, creating directory. Put your old music files here and rerun the command.",
        )
        mkdir(old_music_library)
        exit()

    for directory in [
        new_music_library,
        files_to_keep,
        files_to_remove,
    ]:
        if not path.isdir(directory):
            mkdir(directory)

    # database to be replaced
    old_database, old_file_amt = create_old_database()

    # ytmasc database
    new_database = create_new_database()

    # comparisons
    system("clear")
    for i, data_OLD in enumerate(old_database, start=1):
        scores = []
        old_title = list(data_OLD.items())[0][0]
        old_artist = list(data_OLD.items())[0][1]

        for data_NEW in new_database:
            NEW_title = list(data_NEW.items())[0][0]
            NEW_artist = list(data_NEW.items())[0][1]
            title_score = fuzz.ratio(old_title.lower(), NEW_title.lower())
            artist_score = fuzz.ratio(old_artist.lower(), NEW_artist.lower())
            scores.append(
                {
                    title_score: {
                        "ツ": artist_score,
                        "title": NEW_title,
                        "artist": NEW_artist,
                    }
                }
            )

        file = path.join(old_music_library, f"{old_title}.mp3")
        sorted_data_title = sort_based_on_score(scores, "title_score")
        sorted_data_artist = sort_based_on_score(scores, "artist_score")

        # skip 100 & 100 matches
        if (
            next(iter(sorted_data_title[0])) == 100
            and sorted_data_title[0][next(iter(sorted_data_title[0]))]["ツ"] == 100
        ):
            system("clear")
            print(
                f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nremove: {file}\n"
            )
            rename(file, path.join("!removal", f"{old_title}.mp3"))

        # user decisions
        else:
            print(f"r=remove, k=keep, i=ignore\n")
            table = init_table()
            insert_old_file_data(table, old_title, old_artist, column_to_mark=1)
            insert_rows(sorted_data_title, table, truncate_at=30)
            insert_old_file_data(table, old_title, old_artist, column_to_mark=2)
            insert_rows(sorted_data_artist, table, truncate_at=30)
            print(table)

            input_key = ""
            while input_key not in ["r", "k", "i"]:
                input_key = read_key()
                sleep(0.5)  # temp solution before wait for key up
                # if input_key not in ["r", "k", "i"]:
                #     input_key = ""
                #     system("clear")
                #     print("press h to continue..")
                #     while input_key != "h":
                #         input_key = read_key()
                #         time.sleep(0.5)
                if input_key == "r":
                    system("clear")
                    print(
                        f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nremove: {file}\n"
                    )
                    rename(file, path.join("!remove", f"{old_title}.mp3"))
                elif input_key == "k":
                    system("clear")
                    print(
                        f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nkeep: {file}\n"
                    )
                    rename(file, path.join("!keep", f"{old_title}.mp3"))
                elif input_key == "i":
                    system("clear")
                    print(
                        f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nignore: {file}\n"
                    )
                else:
                    quit()
                    # keyboard doesn't care about terminal focus and i don't know which package would do handle that easily
                    # so, don't multi task? yet?
                # wait for key up
