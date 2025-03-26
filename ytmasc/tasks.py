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
    count_key_amount_in_json,
    current_path,
    download_path,
    fail_log_path,
    library_data_path,
    possible_audio_ext,
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
                    logger.info(f"[FileExistsError] {watch_id + ext} already exists, skipping download.")
                    audio_file_found = True
                    break

            if not audio_file_found:
                logger.info(f"Downloading audio of {watch_id}.")

                try:
                    file.download(url)

                    searched_files = [
                        f
                        for f in os.listdir(os.path.join(current_path, temp_path))
                        if os.path.isfile(os.path.join(os.path.join(current_path, temp_path), f))
                    ]
                    for file in searched_files:
                        for ext in possible_audio_ext:
                            if file[-len(ext) :] == ext:
                                download_filename = file[: -len(ext)]
                                download_ext = file[-len(ext) :]
                                break

                    logger.info(f"Successfully downloaded {watch_id + download_ext}.")

                except FileExistsError:
                    logger.info(f"[FileExistsError] {watch_id + download_ext} already exists, skipping download.")

                except yt_dlp.utils.DownloadError as exception:
                    exception = str(exception)
                    if r"Video unavailable" in exception:
                        logger.warning(f"[JustYouTubeThings] {url} is not available, skipping.")
                        pass
                    elif r"Sign in to confirm you’re not a bot" in exception:
                        logger.warning(f"[JustYouTubeThings] Classified as bot, unable to download {url}.")
                        pass
                    elif r"Sign in to confirm your age" in exception:
                        logger.warning(f"[JustYouTubeThings] Has age restriction, unable to download {url}.")
                        pass
                    elif r"Failed to extract any player response":
                        logger.critical(
                            f"[NoInternetOrElse] yt-dlp was unable to get a response, ensure your internet connection."
                        )
                    else:
                        logger.warning(f"[JustYouTubeThings] Some other error on downloading {url}.")
                        pass
                    return 1, exception

        if os.path.isfile(os.path.join(download_path, watch_id + source_cover_ext)):
            logger.info(f"[FileExistsError] {watch_id + source_cover_ext} already exists, skipping download.")
            cover_file_found = True

        if not cover_file_found:
            try:
                logger.info(f"Downloading {watch_id + source_cover_ext}.")
                try:
                    cover = f"https://img.youtube.com/vi/{watch_id}/maxresdefault.jpg"
                    urllib.request.urlretrieve(
                        cover,
                        os.path.join(temp_path, f"{watch_id + source_cover_ext}"),
                    )
                    logger.info(f"Successfully downloaded {watch_id + source_cover_ext}.")

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
                    # logger.info(f"Successfully downloaded {watch_id + source_cover_ext}.")
                    # except HTTPError:
                    #     exception = HTTPError.reason
                    #     # logger.error(f"[JustYoutubeThings] Couldn't download {watch_id + source_cover_ext}, skipping download.")
                    #     print(exception)
                    #     return 1, exception

                # TODO find out a way to log images that are actually 16:9 (i.e files generated from non-youtube music id's)
                img = PIL.Image.open(os.path.join(os.temp_path, watch_id + source_cover_ext))
                width, height = img.size
                if width % 16 == 0 and height % 9 == 0:
                    area_to_be_cut = (width - height) / 2
                    cropped_img = img.crop((area_to_be_cut, 0, width - area_to_be_cut, height))
                    cropped_img.save(os.path.join(temp_path, watch_id + source_cover_ext))
                    logger.info(f"Successfully cropped {watch_id + source_cover_ext}.")

            except FileExistsError:
                logger.info(f"[FileExistsError] {watch_id + source_cover_ext} already exists, skipping download.")
                pass

        try:
            if not audio_file_found:
                logger.info(f"Moving audio file to {download_path}.")
                os.rename(
                    os.path.join(temp_path, download_filename + download_ext),
                    os.path.join(download_path, watch_id + download_ext),
                )

        except FileExistsError:
            logger.warning(f"[FileExistsError]{watch_id + download_ext} already exists!")
            os.remove(os.path.join(temp_path, download_filename + download_ext))

        except FileNotFoundError:
            logger.warning(f"[FileNotFoundError] {watch_id + download_ext} doesn't exist!")
            pass

        except PermissionError:
            logger.error(f"[PermissionError] {watch_id + download_ext} is in use!")
            pass
            # TODO wait a little then retry?

        try:
            if not cover_file_found:
                logger.info(f"Moving cover file to {download_path}.")
                os.rename(
                    os.path.join(temp_path, watch_id + source_cover_ext),
                    os.path.join(download_path, watch_id + source_cover_ext),
                )
                logger.info(f"Successfully moved files to {download_path}.")
            return 0, 0

        except FileExistsError:
            os.remove(os.path.join(temp_path, watch_id + source_cover_ext))
            logger.warning(f"[FileExistsError] {watch_id + source_cover_ext} file already exists!")

        except FileNotFoundError:
            logger.warning(f"[FileNotFoundError] {watch_id + source_cover_ext} file doesn't exist!")
            pass

        except PermissionError:
            logger.error(
                f"[PermissionError] {watch_id + source_cover_ext} is in use!",
            )
            pass
            # TODO wait a little then retry?

    @staticmethod
    def download_bulk(json: dict):
        fail_amount = 0
        write_txt(fail_log_path, "")

        for i, watch_id in enumerate(json.keys(), start=1):
            logger.info(f"<<< DOWNLOAD {i} >>>")
            fail_state, exception = Tasks.download(watch_id)
            logger.info(f"<<< DOWNLOAD {i} >>>")
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
            logger.info(f"Successfully downloaded all files to {download_path}.")
            pass
        else:
            logger.info(
                f"{fail_amount} out of {i} files couldn't be downloaded. You can check the logs at {fail_log_path}."
            )
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

                logger.info(
                    f"Converting {audio_file} to {output_audio_file}...",
                )
                ffmpeg.input(audio_file_path).output(
                    output_audio_file_path,
                    acodec="libmp3lame",
                    audio_bitrate="192k",  # the max bitrate is 128kbps (with no logins etc.)
                    loglevel="error",
                ).run()
                os.remove(audio_file_path)
                logger.info(f"Successfully converted {audio_file} to {output_audio_file}.")
                return 0
            else:
                logger.warning(f"[FileNotFoundError] {output_audio_file} doesn't exist.")
                return 1
        else:
            logger.warning(f"[FileExistsError] {output_audio_file} already exists, skipping conversion.")
            return 0

    @staticmethod
    def convert_bulk(json: dict):
        fail_amount = 0
        for i, watch_id in enumerate(json.keys(), start=1):
            logger.info(f"<<< CONVERSION {i} >>>")
            fail_state = Tasks.convert(watch_id)
            logger.info(f">>> CONVERSION {i} <<<")
            fail_amount += fail_state

        if not fail_amount:
            logger.info(f"Successfully converted all files in {download_path}.")
            pass
        else:
            logger.info(f"{fail_amount} out of {i} files couldn't be converted.")
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
                f"{audio_file} doesn't exist, skipping tagging. Might be related to YouTube watch_id updates?"
            )
            return 1

    @staticmethod
    def tag_bulk(json: dict):
        "Tag files in bulk"
        fail_amount = 0
        total_operations = count_key_amount_in_json(library_data_path)
        num_digits = len(str(total_operations))
        for i, (watch_id, value) in enumerate(json.items(), start=1):
            logger.info(f"<<< TAG {i} >>>")
            fail_status = Tasks.tag(watch_id, value, num_digits, i - fail_amount)
            logger.info(f">>> TAG {i} <<<")
            fail_amount += fail_status

        if not fail_amount:
            logger.info(f"Successfully tagged all files in {download_path}.")
            pass
        else:
            logger.info(f"{fail_amount} out of {i} files couldn't be tagged.")
            pass
