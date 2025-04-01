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
    current_path,
    download_path,
    fail_log_path,
    get_file_extension,
    get_filename,
    library_data_path,
    possible_audio_ext,
    read_json,
    source_audio_ext,
    source_cover_ext,
    temp_path,
    write_txt,
)

logger = logging.getLogger(__name__)


class Tasks:
    def __init__(self):
        pass

    @staticmethod
    def download(watch_id: str) -> list[str]:
        """
        Downloads files.

        Tries downloading the audio file if it doesn't exist in downloads directory\n
        If it doesn't exist\n
            Downloads audio\n
            If the download is successful\n
                Moves files to downloads directory\n
                Returns 0\n
            If not, returns 1\n

        Tries downloading the cover file if it doesn't exist in downloads directory\n
        Downloads cover\n
        If it doesn't exist\n
            Downloads cover\n
            If the download is successful\n
                Moves files to downloads directory\n
        """

        opt_dict = {
            "extract_audio": True,
            "format": "bestaudio",
            "ignore-errors": True,
            "no-abort-on-error": True,
            "quiet": True,
            "outtmpl": f"{os.path.join(temp_path, watch_id)}.%(audio_ext)s",
            "compat_opts": {"filename-sanitization"},
        }
        audio_file_found = False
        cover_file_found = False
        download_filename = None  # should be the same as watch_id
        download_ext = None

        with yt_dlp.YoutubeDL(opt_dict) as file:
            url = f"https://www.youtube.com/watch?v={watch_id}"

            for ext in possible_audio_ext:
                if os.path.isfile(os.path.join(download_path, watch_id + ext)):
                    audio_file_found = True
                    break

            if not audio_file_found:

                try:
                    file.download(url)

                    searched_files = [
                        f
                        for f in os.listdir(os.path.join(current_path, temp_path))
                        if os.path.isfile(os.path.join(os.path.join(current_path, temp_path), f))
                    ]
                    for file in searched_files:
                        for ext in possible_audio_ext:
                            if "." + get_file_extension(file) == ext:
                                download_filename = get_filename(file)
                                download_ext = "." + get_file_extension(file)
                                break

                except FileExistsError:
                    pass

                except yt_dlp.utils.DownloadError as exception:
                    exception = str(exception)
                    if r"Video unavailable" in exception:
                        pass
                    elif r"Sign in to confirm you’re not a bot" in exception:
                        pass
                    elif r"Sign in to confirm your age" in exception:
                        pass
                    elif r"Failed to extract any player response":
                        pass
                    else:
                        pass
                    return 1, exception

        if os.path.isfile(os.path.join(download_path, watch_id + source_cover_ext)):
            cover_file_found = True

        if not cover_file_found:
            try:
                try:
                    cover = f"https://img.youtube.com/vi/{watch_id}/maxresdefault.jpg"
                    urllib.request.urlretrieve(
                        cover,
                        os.path.join(temp_path, f"{watch_id + source_cover_ext}"),
                    )

                # caused mostly by files generated from non-youtube music id's
                # but this is an inconsistent error, it can happen to youtube music files too, have no idea as to why
                # here's hoping the fallback to always work
                except urllib.error.HTTPError:
                    # try:
                    cover = f"https://img.youtube.com/vi/{watch_id}/hqdefault.jpg"
                    urllib.request.urlretrieve(
                        cover,
                        os.path.join(temp_path, f"{watch_id + source_cover_ext}"),
                    )
                    # except HTTPError:
                    #     exception = HTTPError.reason
                    #     print(exception)
                    #     return 1, exception

                # TODO find out a way to log images that are actually 16:9 (i.e files generated from non-youtube music id's)
                img = PIL.Image.open(os.path.join(temp_path, watch_id + source_cover_ext))
                width, height = img.size
                if width % 16 == 0 and height % 9 == 0:
                    area_to_be_cut = (width - height) / 2
                    cropped_img = img.crop((area_to_be_cut, 0, width - area_to_be_cut, height))
                    cropped_img.save(os.path.join(temp_path, watch_id + source_cover_ext))

            except FileExistsError:
                pass

        try:
            if not audio_file_found:
                os.rename(
                    os.path.join(temp_path, download_filename + download_ext),
                    os.path.join(download_path, watch_id + download_ext),
                )

        except FileExistsError:
            os.remove(os.path.join(temp_path, download_filename + download_ext))

        except FileNotFoundError:
            pass

        try:
            if not cover_file_found:
                os.rename(
                    os.path.join(temp_path, watch_id + source_cover_ext),
                    os.path.join(download_path, watch_id + source_cover_ext),
                )
            return 0, 0

        except FileExistsError:
            os.remove(os.path.join(temp_path, watch_id + source_cover_ext))

        except FileNotFoundError:
            pass

    @staticmethod
    def download_bulk(json_path: str):
        json = read_json(json_path)
        fail_amount = 0
        write_txt(fail_log_path, "")

        for i, watch_id in enumerate(json.keys(), start=1):
            fail_state, exception = Tasks.download(watch_id)
            fail_amount += fail_state
            if exception != 0:
                if (
                    r"Sign in to confirm you’re not a bot" in exception
                    or r"Failed to extract any player response" in exception
                ):
                    break  # sleep?
                # final name for the unique identifier
                append_txt(fail_log_path, exception + "\n")

        if not fail_amount:
            pass
        else:
            pass

    @staticmethod
    def convert(watch_id: str):
        file_name = watch_id
        output_audio_file = os.path.join(file_name + audio_conversion_ext)
        output_audio_file_path = os.path.join(download_path, output_audio_file)

        if not os.path.isfile(output_audio_file_path):
            if os.path.isfile(os.path.join(download_path, file_name + source_audio_ext[0])) or os.path.isfile(
                os.path.join(download_path, file_name + source_audio_ext[1])
            ):
                for ext in source_audio_ext:
                    if os.path.isfile(os.path.join(download_path, file_name + ext)):
                        audio_file = file_name + ext
                        audio_file_path = os.path.join(download_path, audio_file)
                        break

                ffmpeg.input(audio_file_path).output(
                    output_audio_file_path,
                    acodec="libmp3lame",
                    audio_bitrate="192k",  # the max bitrate is 128kbps (with no logins etc.)
                    loglevel="error",
                ).run()
                os.remove(audio_file_path)
                return 0
            else:
                return 1
        else:
            return 0

    @staticmethod
    def convert_bulk(json_path: str):
        json = read_json(json_path)
        fail_amount = 0
        for i, watch_id in enumerate(json.keys(), start=1):
            fail_state = Tasks.convert(watch_id)
            fail_amount += fail_state

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

        try:
            audio_file = eyed3.load(audio_file_path)
            audio_file.initTag()

            # if audio_file is not None and audio_file.tag is not None:  # true
            #     if watch_id in json:  # true
            audio_file.tag.title = title
            audio_file.tag.artist = value["artist"]
            audio_file.tag.album = order_number
            with open(cover_file_path, "rb") as cover_art:
                audio_file.tag.images.set(3, cover_art.read(), "image/jpeg")

            audio_file.tag.save()
            return 0

        except FileNotFoundError:
            return 1

        except OSError:
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

        if not fail_amount:
            pass
        else:
            pass
