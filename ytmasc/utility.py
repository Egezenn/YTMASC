"Stores all the values required, provides base functions that NOT use these values."

import glob
import json
import logging
import os

import pandas

current_path = os.getcwd()

data_path = r"data"
download_path = r"downloads"
temp_path = r"temp"

csv_library_data = r"library.csv"
fail_log = r"fails.txt"
library_data = r"library.json"
library_page = r"libraryPage.htm"
log = r"log.txt"

audio_conversion_ext = r".mp3"
possible_audio_ext = [r".webm", r".m4a", r".mp3"]
source_audio_ext = [r".webm", r".m4a"]
source_cover_ext = r".jpg"

csv_library_data_path = os.path.join(data_path, csv_library_data)
fail_log_path = os.path.join(data_path, fail_log)
library_data_path = os.path.join(data_path, library_data)
library_page_path = os.path.join(data_path, library_page)


def setup_logging(verbosity):
    if verbosity == "d":
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(name)s - %(funcName)s - %(levelname)s - %(message)s",
            filename=log,
            filemode="w",
        )
    elif verbosity == "i":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(name)s - %(funcName)s - %(levelname)s - %(message)s",
            filename=log,
            filemode="w",
        )
    elif verbosity == "w":
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s | %(name)s - %(funcName)s - %(levelname)s - %(message)s",
            filename=log,
        )
    elif verbosity == "e":
        logging.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s | %(name)s - %(funcName)s - %(levelname)s - %(message)s",
            filename=log,
            filemode="w",
        )
    elif verbosity == "c":
        logging.basicConfig(
            level=logging.CRITICAL,
            format="%(asctime)s | %(name)s - %(funcName)s - %(levelname)s - %(message)s",
            filename=log,
            filemode="w",
        )


def check_if_directories_exist_and_make_if_not(*directories: str):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def sort_dictionary_based_on_key(dictionary: dict) -> dict:
    return dict(sorted(dictionary.items(), key=lambda item: item[0].lower()))


def sort_nested(
    dictionary: dict,
) -> dict:
    "Sorts dictionary based on the value inside nested dictionary's second key's value"
    return dict(sorted(dictionary.items(), key=lambda item: list(item[1].values())[1].lower()))


def convert_json_to_csv(json_file: str, csv_file: str):
    df = pandas.read_json(json_file)
    df_transposed = df.transpose().reset_index()
    df_transposed.to_csv(csv_file, index=False)


def convert_csv_to_json(csv_file: str, json_file: str):
    df = pandas.read_json(csv_file)
    df.set_index("index", inplace=True)
    df.fillna("", inplace=True)
    json_data = df.to_dict(orient="index")
    with open(json_file, "w") as f:
        json.dump(json_data, f, indent=2)


def read_json(file_path: str) -> dict:
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}


def write_json(file_path: str, data: dict):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)


def update_json(file_path: str, data: dict):
    existing_data = read_json(file_path)
    for key, value in data.items():
        if key not in existing_data:
            existing_data[key] = value
    data = sort_nested(existing_data)
    write_json(file_path, data)


def write_txt(file_path: str, data: str):
    with open(file_path, "w") as file:
        file.write(data)


def read_txt(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def read_txt_as_list(file_path: str) -> list:
    with open(file_path, "r") as file:
        lines = [line.strip() for line in file]
    return lines


def append_txt(file_path: str, data: str):
    with open(file_path, "a") as file:
        file.write(data)


def count_files(directory: str, extensions: list[str]) -> int:
    count = 0
    for extension in extensions:
        pattern = os.path.join(directory, f"*{extension}")
        files = glob(pattern)
        count += len(files)
    return count


def count_key_amount_in_json(file_path: str) -> int:
    return len(read_json(file_path))


def zfill_progress(num: int, reference: int) -> str:
    return f"{str(num).zfill(len(str(reference)))}/{str(reference)}"


# only one dot files
def get_filename(string: str) -> str:
    return string.split(".")[0]


def get_file_extension(string: str) -> str:
    return string.split(".")[1]
