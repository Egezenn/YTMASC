"Provides conversion functions for unwanted formats."
from os import path, remove
from logging import getLogger

from ffmpeg import input as finput

from ytmasc.utility import (
    audio_conversion_ext,
    download_path,
    source_audio_ext,
)

logger = getLogger(__name__)


def convert_bulk(json: dict):
    "Converts source source_audio_ext to audio_conversion_ext in bulk."
    fail_amount = 0
    for i, key in enumerate(json.keys(), start=1):
        logger.info(f"<<< CONVERSION {i} >>>")
        fail_state = convert(key)
        logger.info(f">>> CONVERSION {i} <<<")
        fail_amount += fail_state

    if not fail_amount:
        logger.info(f"Successfully converted all files in {download_path}.")
        pass
    else:
        logger.info(f"{fail_amount} out of {i} files couldn't be converted.")
        pass


def convert(key: str):
    "Converts source source_audio_ext to audio_conversion_ext."

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

            logger.info(
                f"Converting {audio_file} to {output_audio_file}...",
            )
            finput(audio_file_path).output(
                output_audio_file_path,
                acodec="libmp3lame",
                audio_bitrate="192k",  # the max bitrate is 128kbps (with no logins etc.)
                loglevel="error",
            ).run()
            remove(audio_file_path)
            logger.info(f"Successfully converted {audio_file} to {output_audio_file}.")
            return 0
        else:
            logger.warning(f"[FileNotFoundError] {output_audio_file} doesn't exist.")
            return 1
    else:
        logger.warning(
            f"[FileExistsError] {output_audio_file} already exists, skipping conversion."
        )
        return 0
