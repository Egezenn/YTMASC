"Provides conversion functions for unwanted formats."
from inspect import currentframe
from os import path, remove

from ffmpeg import input as finput

from ytmasc.utility import (
    audio_conversion_ext,
    debug_print,
    download_path,
    get_current_file,
    get_current_function,
    source_audio_ext,
)

current_file = get_current_file(__file__)


def convert_bulk(json: dict):
    "Converts source source_audio_ext to audio_conversion_ext in bulk."
    current_function = get_current_function(currentframe())
    fail_amount = 0
    for i, key in enumerate(json.keys(), start=1):
        debug_print(
            current_file,
            current_function,
            "task",
            "CONVERSION",
            num=i,
            position="start",
        )
        fail_state = convert(key)
        debug_print(
            current_file, current_function, "task", "CONVERSION", num=i, position="end"
        )
        fail_amount += fail_state

    if not fail_amount:
        debug_print(
            current_file,
            current_function,
            "i",
            f"Successfully converted all files in {download_path}.",
        )
    else:
        debug_print(
            current_file,
            current_function,
            "i",
            f"{fail_amount} out of {i} files couldn't be converted.",
        )


def convert(key: str):
    "Converts source source_audio_ext to audio_conversion_ext."
    current_function = get_current_function(currentframe())

    file_name = key
    output_audio_file = path.join(file_name + audio_conversion_ext)
    output_audio_file_path = path.join(download_path, output_audio_file)

    if not path.isfile(output_audio_file_path):
        if path.isfile(
            path.join(download_path, file_name + source_audio_ext[0])
        ) or path.isfile(path.join(download_path, file_name + source_audio_ext[1])):
            for ext in source_audio_ext:
                if path.isfile(path.join(download_path, file_name + ext)):
                    audio_file = file_name + ext
                    audio_file_path = path.join(download_path, audio_file)
                    break

            debug_print(
                current_file,
                current_function,
                "i",
                f"Converting {audio_file} to {output_audio_file}...",
            )
            finput(audio_file_path).output(
                output_audio_file_path,
                acodec="libmp3lame",
                audio_bitrate="192k",  # the max bitrate is 128kbps (with no logins etc.)
                loglevel="error",
            ).run()
            remove(audio_file_path)
            debug_print(
                current_file,
                current_function,
                "i",
                f"Successfully converted {audio_file} to {output_audio_file}.",
            )
            return 0
        else:
            debug_print(
                current_file,
                current_function,
                "w",
                f"{output_audio_file} doesn't exist.",
                error_type="FileNotFoundError",
            )
            return 1
    else:
        debug_print(
            current_file,
            current_function,
            "w",
            f"{output_audio_file} already exists, skipping conversion.",
            error_type="FileExistsError",
        )
        return 0
