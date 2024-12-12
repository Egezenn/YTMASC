"Imports an old database and compares each file with new ones."
import os
import time

from fuzzywuzzy import fuzz
from keyboard import read_key

from ytmasc.dbtools.matcher_utils import (
    NEW_music_library,
    OLD_music_library,
    create_new_database,
    create_old_database,
    files_to_keep,
    files_to_remove,
    init_table,
    insert_old_file_data,
    insert_rows,
    sort_based_on_score,
)

if __name__ == "__main__":
    for directory in [
        OLD_music_library,
        NEW_music_library,
        files_to_keep,
        files_to_remove,
    ]:
        if not os.path.isdir(directory):
            os.mkdir(directory)

    # database to be replaced
    OLD_DATABASE, old_file_amt = create_old_database()

    # ytmasc database
    NEW_DATABASE = create_new_database()

    # comparisons
    os.system("clear")
    for i, data_OLD in enumerate(OLD_DATABASE, start=1):
        scores = []
        OLD_title = list(data_OLD.items())[0][0]
        OLD_artist = list(data_OLD.items())[0][1]

        for data_NEW in NEW_DATABASE:
            NEW_title = list(data_NEW.items())[0][0]
            NEW_artist = list(data_NEW.items())[0][1]
            title_score = fuzz.ratio(OLD_title.lower(), NEW_title.lower())
            artist_score = fuzz.ratio(OLD_artist.lower(), NEW_artist.lower())
            scores.append(
                {
                    title_score: {
                        "ツ": artist_score,
                        "title": NEW_title,
                        "artist": NEW_artist,
                    }
                }
            )

        file = os.path.join(OLD_music_library, f"{OLD_title}.mp3")
        sorted_data_title = sort_based_on_score(scores, "title_score")
        sorted_data_artist = sort_based_on_score(scores, "artist_score")

        # skip 100 & 100 matches
        if (
            next(iter(sorted_data_title[0])) == 100
            and sorted_data_title[0][next(iter(sorted_data_title[0]))]["ツ"] == 100
        ):
            os.system("clear")
            print(
                f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nremove: {file}\n"
            )
            os.rename(file, os.path.join("!removal", f"{OLD_title}.mp3"))

        # user decisions
        else:
            print(f"r=remove, k=keep, i=ignore\n")
            table = init_table()
            insert_old_file_data(table, OLD_title, OLD_artist, column_to_mark=1)
            insert_rows(sorted_data_title, table, truncate_at=30)
            insert_old_file_data(table, OLD_title, OLD_artist, column_to_mark=2)
            insert_rows(sorted_data_artist, table, truncate_at=30)
            print(table)

            input_key = ""
            while input_key not in ["r", "k", "i"]:
                input_key = read_key()
                time.sleep(0.5)  # temp solution before wait for key up
                # if input_key not in ["r", "k", "i"]:
                #     input_key = ""
                #     os.system("clear")
                #     print("press h to continue..")
                #     while input_key != "h":
                #         input_key = read_key()
                #         time.sleep(0.5)
                if input_key == "r":
                    os.system("clear")
                    print(
                        f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nremove: {file}\n"
                    )
                    os.rename(file, os.path.join("!remove", f"{OLD_title}.mp3"))
                elif input_key == "k":
                    os.system("clear")
                    print(
                        f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nkeep: {file}\n"
                    )
                    os.rename(file, os.path.join("!keep", f"{OLD_title}.mp3"))
                elif input_key == "i":
                    os.system("clear")
                    print(
                        f"{str(i).zfill(len(str(old_file_amt)))}/{old_file_amt}\nignore: {file}\n"
                    )
                else:
                    quit()
                    # keyboard doesn't care about terminal focus and i don't know which package would do handle that easily
                    # so, don't multi task? yet?
                # wait for key up
