from logging import getLogger
from os import listdir, path, remove, rename
from re import search
from urllib.error import HTTPError
from urllib.request import urlretrieve

from PIL import Image
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from ytmasc.utility import (
    append_txt,
    current_path,
    download_path,
    fail_log_path,
    possible_audio_ext,
    source_cover_ext,
    temp_path,
    write_txt,
)

logger = getLogger(__name__)


def download_bulk(json: dict):
    fail_amount = 0
    write_txt(fail_log_path, "")

    for i, watch_id in enumerate(json.keys(), start=1):
        logger.info(f"<<< DOWNLOAD {i} >>>")
        fail_state, exception = download(watch_id)
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
        "outtmpl": f"{path.join(temp_path, watch_id)}.%(audio_ext)s",
        "compat_opts": {"filename-sanitization"},
    }
    audio_file_found = False
    cover_file_found = False
    download_filename = None  # should be the same as watch_id
    download_ext = None

    with YoutubeDL(opt_dict) as file:
        url = f"https://www.youtube.com/watch?v={watch_id}"

        for ext in possible_audio_ext:
            if path.isfile(path.join(download_path, watch_id + ext)):
                logger.info(
                    f"[FileExistsError] {watch_id + ext} already exists, skipping download."
                )
                audio_file_found = True
                break

        if not audio_file_found:
            logger.info(f"Downloading audio of {watch_id}.")

            try:
                file.download(url)

                searched_files = [
                    f
                    for f in listdir(path.join(current_path, temp_path))
                    if path.isfile(path.join(path.join(current_path, temp_path), f))
                ]
                for file in searched_files:
                    for ext in possible_audio_ext:
                        if file[-len(ext) :] == ext:
                            download_filename = file[: -len(ext)]
                            download_ext = file[-len(ext) :]
                            break

                logger.info(f"Successfully downloaded {watch_id + download_ext}.")

            except FileExistsError:
                logger.info(
                    f"[FileExistsError] {watch_id + download_ext} already exists, skipping download."
                )

            except DownloadError as exception:
                exception = str(exception)
                if r"Video unavailable" in exception:
                    logger.warning(
                        f"[JustYouTubeThings] {url} is not available, skipping."
                    )
                    pass
                elif r"Sign in to confirm you’re not a bot" in exception:
                    logger.warning(
                        f"[JustYouTubeThings] Classified as bot, unable to download {url}."
                    )
                    pass
                elif r"Sign in to confirm your age" in exception:
                    logger.warning(
                        f"[JustYouTubeThings] Has age restriction, unable to download {url}."
                    )
                    pass
                elif r"Failed to extract any player response":
                    logger.critical(
                        f"[NoInternetOrElse] yt-dlp was unable to get a response, ensure your internet connection."
                    )
                else:
                    logger.warning(
                        f"[JustYouTubeThings] Some other error on downloading {url}."
                    )
                    pass
                return 1, exception

    if path.isfile(path.join(download_path, watch_id + source_cover_ext)):
        logger.info(
            f"[FileExistsError] {watch_id + source_cover_ext} already exists, skipping download."
        )
        cover_file_found = True

    if not cover_file_found:
        try:
            logger.info(f"Downloading {watch_id + source_cover_ext}.")
            try:
                cover = f"https://img.youtube.com/vi/{watch_id}/maxresdefault.jpg"
                urlretrieve(
                    cover, path.join(temp_path, f"{watch_id + source_cover_ext}")
                )
                logger.info(f"Successfully downloaded {watch_id + source_cover_ext}.")

            # caused mostly by files generated from non-youtube music id's
            # but this is an inconsistent error, it can happen to youtube music files too, have no idea as to why
            # here's hoping the fallback to always work
            except HTTPError:
                # try:
                cover = f"https://img.youtube.com/vi/{watch_id}/hqdefault.jpg"
                urlretrieve(
                    cover, path.join(temp_path, f"{watch_id + source_cover_ext}")
                )
                # logger.info(f"Successfully downloaded {watch_id + source_cover_ext}.")
                # except HTTPError:
                #     exception = HTTPError.reason
                #     # logger.error(f"[JustYoutubeThings] Couldn't download {watch_id + source_cover_ext}, skipping download.")
                #     print(exception)
                #     return 1, exception

            # TODO find out a way to log images that are actually 16:9 (i.e files generated from non-youtube music id's)
            img = Image.open(path.join(temp_path, watch_id + source_cover_ext))
            width, height = img.size
            if width % 16 == 0 and height % 9 == 0:
                area_to_be_cut = (width - height) / 2
                cropped_img = img.crop(
                    (area_to_be_cut, 0, width - area_to_be_cut, height)
                )
                cropped_img.save(path.join(temp_path, watch_id + source_cover_ext))
                logger.info(f"Successfully cropped {watch_id + source_cover_ext}.")

        except FileExistsError:
            logger.info(
                f"[FileExistsError] {watch_id + source_cover_ext} already exists, skipping download."
            )
            pass

    try:
        if not audio_file_found:
            logger.info(f"Moving audio file to {download_path}.")
            rename(
                path.join(temp_path, download_filename + download_ext),
                path.join(download_path, watch_id + download_ext),
            )

    except FileExistsError:
        logger.warning(f"[FileExistsError]{watch_id + download_ext} already exists!")
        remove(path.join(temp_path, download_filename + download_ext))

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
            rename(
                path.join(temp_path, watch_id + source_cover_ext),
                path.join(download_path, watch_id + source_cover_ext),
            )
            logger.info(f"Successfully moved files to {download_path}.")
        return 0, 0

    except FileExistsError:
        remove(path.join(temp_path, watch_id + source_cover_ext))
        logger.warning(
            f"[FileExistsError] {watch_id + source_cover_ext} file already exists!"
        )

    except FileNotFoundError:
        logger.warning(
            f"[FileNotFoundError] {watch_id + source_cover_ext} file doesn't exist!"
        )
        pass

    except PermissionError:
        logger.error(
            f"[PermissionError] {watch_id + source_cover_ext} is in use!",
        )
        pass
        # TODO wait a little then retry?
