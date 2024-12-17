"Provides tagging functions for the desired files."
from logging import getLogger
from os import path

from eyed3 import load as loadmp3

from ytmasc.utility import (
    audio_conversion_ext,
    count_files,
    download_path,
    possible_audio_ext,
    source_cover_ext,
)

logger = getLogger(__name__)


def tag_bulk(json: dict):
    "Tag files in bulk using tag()"
    fail_amount = 0
    total_files = count_files(download_path, possible_audio_ext)
    num_digits = len(str(total_files))
    for i, (key, value) in enumerate(json.items(), start=1):

        logger.info(f"<<< TAG {i} >>>")
        fail_status = tag(key, value, num_digits, i - fail_amount)
        logger.info(f">>> TAG {i} <<<")
        fail_amount += fail_status

    if not fail_amount:
        logger.info(f"Successfully tagged all files in {download_path}.")
        pass
    else:
        logger.info(f"{fail_amount} out of {i} files couldn't be tagged.")
        pass


def tag(key, value, digit_amount, num):
    "Tag a file with title, artist, album(order_number), cover art"
    file_name = key
    title = value["title"]
    artist = value["artist"]
    audio_file = file_name + audio_conversion_ext
    audio_file_path = path.join(download_path, audio_file)
    order_number = str(num).zfill(digit_amount)
    cover_file = file_name + source_cover_ext
    cover_file_path = path.join(download_path, cover_file)

    try:
        audio_file = loadmp3(audio_file_path)
        audio_file.initTag()

        # if audio_file is not None and audio_file.tag is not None:  # true
        #     if key in json:  # true
        logger.info(
            f"Tagging {audio_file} with:\n"
            f"\ttitle:\t{title}\n"
            f"\tartist:\t{artist}\n"
            f"\talbum:\t{order_number}\n"
            f"\tcover:\t{cover_file}",
        )
        audio_file.tag.title = title
        audio_file.tag.artist = value["artist"]
        audio_file.tag.album = order_number
        with open(cover_file_path, "rb") as cover_art:
            audio_file.tag.images.set(3, cover_art.read(), "image/jpeg")

        audio_file.tag.save()
        logger.info(f"Successfully tagged {audio_file}.")
        return 0

    except FileNotFoundError:
        logger.warning(f"{audio_file} doesn't exist, skipping tagging.")
        return 1

    except OSError:
        logger.warning(
            f"{audio_file} doesn't exist, skipping tagging. Might be related to YouTube key updates?"
        )
        return 1
