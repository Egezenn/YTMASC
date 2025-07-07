"Audio and image file related functions"

import logging
import os
import urllib.error
import urllib.request

import eyed3
import ffmpeg
import PIL
import yt_dlp
import yt_dlp.utils

from ytmasc.utility import (
    append_txt,
    audio_conversion_ext,
    count_key_in_json,
    download_path,
    fail_log_path,
    library_data_path,
    possible_audio_ext,
    read_json,
    source_audio_ext,
    source_cover_ext,
    write_txt,
)

logger = logging.getLogger(__name__)


class Tasks:
    def __init__(self):
        pass

    @staticmethod
    def download(watch_id: str) -> list[Exception]:
        exceptions = []
        opt_dict = {
            "extract_audio": True,
            "format": "bestaudio",
            "ignore-errors": True,
            "no-abort-on-error": True,
            "quiet": True,
            "outtmpl": f"{os.path.join(download_path, watch_id)}.%(audio_ext)s",
            "compat_opts": {"filename-sanitization"},
        }
        audio_file_found = False
        cover_file_found = False

        for ext in possible_audio_ext:
            if os.path.isfile(os.path.join(download_path, watch_id + ext)):
                audio_file_found = True
                break
        if os.path.isfile(os.path.join(download_path, watch_id + source_cover_ext)):
            cover_file_found = True

        if not audio_file_found:
            url = f"https://www.youtube.com/watch?v={watch_id}"
            try:
                with yt_dlp.YoutubeDL(opt_dict) as file:
                    file.download(url)

            except yt_dlp.utils.DownloadError as e:
                e_str = str(e)
                if r"Video unavailable" in e_str:
                    pass
                elif r"Sign in to confirm you’re not a bot" in e_str:
                    pass
                elif r"Sign in to confirm your age" in e_str:
                    pass
                elif r"Failed to extract any player response":
                    pass
                else:
                    exceptions.append({type(e).__name__: e_str})

        if not cover_file_found:
            try:
                cover = f"https://img.youtube.com/vi/{watch_id}/maxresdefault.jpg"
                urllib.request.urlretrieve(
                    cover,
                    os.path.join(download_path, f"{watch_id + source_cover_ext}"),
                )

            # caused mostly by files generated from non-youtube music id's
            # but this is an inconsistent error, it can happen to youtube music files too, have no idea as to why
            # here's hoping the fallback to always work
            except urllib.error.HTTPError:
                try:
                    cover = f"https://img.youtube.com/vi/{watch_id}/hqdefault.jpg"
                    urllib.request.urlretrieve(
                        cover,
                        os.path.join(download_path, f"{watch_id + source_cover_ext}"),
                    )
                except Exception as e:
                    exceptions.append({type(e).__name__: str(e)})

            # TODO find images that are actually 16:9 and keep its ratio (i.e files generated from non-youtube music id's)
            # need to solve color similarity from jpeg compression
            img = PIL.Image.open(os.path.join(download_path, watch_id + source_cover_ext))
            width, height = img.size
            if width % 16 == 0 and height % 9 == 0:
                area_to_be_cut = (width - height) / 2
                cropped_img = img.crop((area_to_be_cut, 0, width - area_to_be_cut, height))
                cropped_img.save(os.path.join(download_path, watch_id + source_cover_ext))

        return exceptions

    @staticmethod
    def download_bulk(json_path: str, skip=None):
        json = read_json(json_path)
        write_txt(fail_log_path, "")
        break_loop = False

        for watch_id in json.keys():
            if skip and watch_id != skip:
                continue
            elif watch_id == skip:
                skip = None

            logger.info(f"Currently downloading {watch_id}")
            exceptions = Tasks.download(watch_id)

            if exceptions:
                for exception_name, exception_string in exceptions.items():
                    if (
                        r"Sign in to confirm you’re not a bot" in exception_string
                        or r"Failed to extract any player response" in exception_string
                    ):
                        break_loop = True
                    append_txt(fail_log_path, f"{exception_name}: {exception_string} \n")

            if break_loop:
                break

    # TODO Use filelist and then pull the data
    @staticmethod
    def convert(watch_id: str):
        file_name = watch_id
        output_audio_file = os.path.join(file_name + audio_conversion_ext)
        output_audio_file_path = os.path.join(download_path, output_audio_file)

        source_file_exists = False

        for ext in source_audio_ext:
            if os.path.isfile(os.path.join(download_path, file_name + ext)):
                source_file_exists = True
                source_audio_file = file_name + ext
                source_audio_file_path = os.path.join(download_path, source_audio_file)
                break

        if not os.path.isfile(output_audio_file_path) and source_file_exists:
            # the max bitrate is 64kbps webm (with no logins etc.)
            # which roughly translates to 2x+~ rate to mitigate conversion losses
            ffmpeg.input(source_audio_file_path).output(
                output_audio_file_path,
                acodec="libmp3lame",
                audio_bitrate="192k",
                loglevel="error",
            ).run()
            os.remove(source_audio_file_path)

    @staticmethod
    def convert_bulk(json_path: str):
        json = read_json(json_path)
        fail_amount = 0
        for i, watch_id in enumerate(json.keys(), start=1):
            Tasks.convert(watch_id)

        if not fail_amount:
            pass
        else:
            pass

    @staticmethod
    def tag(watch_id, value, digit_amount, num):
        "Tag a file with title, artist, album(zero filled integers), cover art"
        file_name = watch_id
        title = value["title"]
        artist = value["artist"]
        audio_file = file_name + audio_conversion_ext
        audio_file_path = os.path.join(download_path, audio_file)
        order_number = str(num).zfill(digit_amount)
        cover_file = file_name + source_cover_ext
        cover_file_path = os.path.join(download_path, cover_file)

        if os.path.isfile(audio_file_path):
            audio_file = eyed3.load(audio_file_path)
            audio_file.initTag()

            audio_file.tag.title = title
            audio_file.tag.artist = artist
            audio_file.tag.album = order_number
            with open(cover_file_path, "rb") as cover_art:
                audio_file.tag.images.set(3, cover_art.read(), "image/jpeg")

            audio_file.tag.save()

            return 0

        else:
            return 1

    @staticmethod
    def tag_bulk(json_path: str):
        json = read_json(json_path)
        "Tag files in bulk"
        fail_amount = 0
        total_operations = count_key_in_json(library_data_path)
        num_digits = len(str(total_operations))
        for i, (watch_id, value) in enumerate(json.items(), start=1):
            fail_status = Tasks.tag(watch_id, value, num_digits, i - fail_amount)
            fail_amount += fail_status
