"Stores all the values required, provides base functions that NOT use these values."
from glob import glob
from inspect import getframeinfo
from json import dump as jdump
from json import load as jload
from os import getcwd, makedirs, path

from pandas import read_csv as pread_csv
from pandas import read_json as pread_json
from yaml import FullLoader
from yaml import dump as ydump
from yaml import load as yload

debug = True
current_path = getcwd()

data_path = r"data"
download_path = r"downloads"
temp_path = r"temp"

csv_library_data = r"library.csv"
fail_log = r"fails.txt"
library_data = r"library.json"
library_page = r"libraryPage.htm"
yaml_config = r"config.yaml"

audio_conversion_ext = r".mp3"
possible_audio_ext = [r".webm", r".m4a", r".mp3"]
source_audio_ext = [r".webm", r".m4a"]
source_cover_ext = r".jpg"

csv_library_data_path = path.join(data_path, csv_library_data)
fail_log_path = path.join(data_path, fail_log)
library_data_path = path.join(data_path, library_data)
library_page_path = path.join(data_path, library_page)


def get_current_file(file: str):
    "Provides context as to which module is doing stuff"
    return path.basename(file.split(".")[0])


def get_current_function(frame):
    "Provides context as to which function is doing stuff"
    return getframeinfo(frame).function


class Formatting:
    "Shorthand for terminal formatting sequences"
    PURPLE = "\x1b[95m"
    LIGHTBLUE = "\x1b[94m"
    CYAN = "\x1b[96m"
    GREEN = "\x1b[92m"
    YELLOW = "\x1b[93m"
    RED = "\x1b[91m"
    BOLD = "\x1b[1m"
    UNDERLINE = "\x1b[4m"
    ENDFORMATTING = "\x1b[0m"


def debug_print(
    curr_file: str, curr_func: str, message_type: str, message: str, **kwargs: int | str
):
    "Prints stuff so we know what's going on"
    if debug:
        if (
            message_type == "task"
            and kwargs.get("num") is not None
            and (kwargs.get("position") == "start")
        ):
            print(
                f"{Formatting.PURPLE}{Formatting.BOLD}{Formatting.UNDERLINE}/////////// {message} TASK({kwargs.get('num')}) \\\\\\\\\\\\\\\\\\\\\\{Formatting.ENDFORMATTING}"
            )
        elif message_type == "task" and kwargs.get("num") is not None:
            if kwargs.get("position") == "end":
                print(
                    f"{Formatting.PURPLE}{Formatting.BOLD}{Formatting.UNDERLINE}\\\\\\\\\\\\\\\\\\\\\\ {message} TASK({kwargs.get('num')}) ///////////\n{Formatting.ENDFORMATTING}"
                )
        else:
            formatting_string = ""
            if message_type == "i":
                message_type = "INFO"
                formatting_string += Formatting.CYAN
            elif message_type == "e":
                message_type = f"ERROR-{kwargs.get('error_type')}"
                formatting_string += Formatting.YELLOW
            elif message_type == "w":  # unused
                message_type = "WARNING"

            if kwargs.get("purple"):
                formatting_string += Formatting.PURPLE
            elif kwargs.get("lightblue"):
                formatting_string += Formatting.LIGHTBLUE
            elif kwargs.get("cyan"):
                formatting_string += Formatting.CYAN
            elif kwargs.get("green"):
                formatting_string += Formatting.GREEN
            elif kwargs.get("yellow"):
                formatting_string += Formatting.YELLOW
            elif kwargs.get("red"):
                formatting_string += Formatting.RED
            if kwargs.get("bold"):
                formatting_string += Formatting.BOLD
            if kwargs.get("underline"):
                formatting_string += Formatting.UNDERLINE
            print(
                f"{formatting_string}[{curr_file}-{curr_func}-{message_type}] {message}{Formatting.ENDFORMATTING}"
            )


def check_if_directories_exist_and_make_if_not(*directories: str):
    "Used at initialization"
    for directory in directories:
        makedirs(directory, exist_ok=True)


def sortDictionaryBasedOnKey(dictionary: dict) -> dict:
    "Unused"
    return dict(sorted(dictionary.items(), key=lambda item: item[0].lower()))


def sort_dictionary_based_on_value_inside_nested_dictionary(
    dictionary: dict,
) -> dict:
    "Used for storing dictionary data in ascending order depending on title"
    return dict(
        sorted(dictionary.items(), key=lambda item: list(item[1].values())[1].lower())
    )


def convert_json_to_csv(json_file: str, csv_file: str):
    df = pread_json(json_file)
    df_transposed = df.transpose().reset_index()
    df_transposed.to_csv(csv_file, index=False)


def convert_csv_to_json(csv_file: str, json_file: str):
    df = pread_csv(csv_file)
    df.set_index("index", inplace=True)
    df.fillna("", inplace=True)
    json_data = df.to_dict(orient="index")
    with open(json_file, "w") as f:
        jdump(json_data, f, indent=2)


def read_json(file_path: str) -> dict:
    "Used whenever something runs"
    try:
        with open(file_path, "r") as json_file:
            return jload(json_file)
    except FileNotFoundError:
        return {}


def write_json(file_path: str, data: dict):
    "Used whenever saving"
    with open(file_path, "w") as json_file:
        jdump(data, json_file, indent=2)


def update_json(file_path: str, data: dict):
    "Used in appending unique data to library"
    existing_data = read_json(file_path)
    for key, value in data.items():
        if key not in existing_data:
            existing_data[key] = value
    data = sort_dictionary_based_on_value_inside_nested_dictionary(existing_data)
    write_json(file_path, data)


def read_yaml(file_path: str) -> dict:
    "Used whenever something runs"
    try:
        with open(file_path, "r") as file:
            return yload(file, Loader=FullLoader)
    except FileNotFoundError:
        return {}


def update_yaml(file_path: str, data: dict):
    "Used whenever a value is changed"
    with open(file_path, "w") as file:
        ydump(data, file, default_flow_style=False)


def write_txt(file_path: str, data: str):
    "Used for fail logs"
    with open(file_path, "w") as file:
        file.write(data)


def read_txt(file_path: str) -> str:
    "Used for fail logs"
    with open(file_path, "r") as file:
        return file.read()


def append_txt(file_path: str, data: str):
    "Used for fail logs"
    with open(file_path, "a") as file:
        file.write(data)


def count_files(directory: str, extensions: list[str]) -> int:
    "Used for album naming"
    count = 0
    for extension in extensions:
        pattern = path.join(directory, f"*{extension}")
        files = glob(pattern)
        count += len(files)
    return count
