"Provides functions to fetch all the desired files."
from os import listdir, path, remove, rename
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


def download_bulk(json: dict):
    "Downloads files in bulk."
    fail_amount = 0
    write_txt(fail_log_path, "")

    for i, key in enumerate(json.keys(), start=1):
        # debug_print(
        #     current_file, current_function, "task", "DOWNLOAD", num=i, position="start"
        # )
        fail_state, exception = download(key)
        # debug_print(
        #     current_file, current_function, "task", "DOWNLOAD", num=i, position="end"
        # )
        fail_amount += fail_state
        if exception != 0:
            if r"Sign in to confirm you’re not a bot" in exception:
                break  # sleep?
            append_txt(fail_log_path, exception + "\n")

    if not fail_amount:
        pass
        # debug_print("i",
        #     f"Successfully downloaded all files to {download_path}.",
        # )
    else:
        pass
        # debug_print("i",
        #     f"{fail_amount} out of {i} files couldn't be downloaded. You can check the logs at {fail_log_path}.",
        # )


# TODO return more things if things blow up
def download(key: str) -> list[str]:
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
        "outtmpl": f"{path.join(temp_path, key)}.%(audio_ext)s",
        "compat_opts": {"filename-sanitization"},
    }
    audio_file_found = False
    cover_file_found = False
    download_filename = None  # should be the same as key
    download_ext = None

    with YoutubeDL(opt_dict) as file:
        url = f"https://www.youtube.com/watch?v={key}"

        for ext in possible_audio_ext:
            if path.isfile(path.join(download_path, key + ext)):
                # debug_print("i",
                #     f"{key + ext} already exists, skipping download.",
                #     error_type="FileExistsError",
                # )
                audio_file_found = True
                break

        if not audio_file_found:
            # debug_print(
            #     current_file, current_function, "i", f"Downloading audio of {key}."
            # )

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

                # debug_print("i",
                #     f"Successfully downloaded {key + download_ext}.",
                # )

            except FileExistsError:
                pass
                # debug_print("i",
                #     f"{key + download_ext} already exists, skipping download.",
                #     error_type="FileExistsError",
                # )

            except DownloadError as exception:
                exception = str(exception)
                if "Video unavailable" in exception:
                    pass
                    # debug_print("w",
                    #     f"{url} is not available, skipping.",
                    #     error_type="JustYouTubeThings",
                    # )
                elif "Sign in to confirm you’re not a bot" in exception:
                    pass
                    # debug_print("w",
                    #     f"Classified as bot, unable to download {url}.",
                    #     error_type="JustYouTubeThings",
                    # )
                elif "Sign in to confirm your age" in exception:
                    pass
                    # debug_print("w",
                    #     f"Classified as bot, unable to download {url}.",
                    #     error_type="JustYouTubeThings",
                    # )
                else:
                    pass
                    # debug_print("w",
                    #     f"Some other error on downloading {url}.",
                    #     error_type="JustYouTubeThings",
                    # )
                return 1, exception

    if path.isfile(path.join(download_path, key + source_cover_ext)):
        # debug_print("i",
        #     f"{key + source_cover_ext} already exists, skipping download.",
        #     error_type="FileExistsError",
        # )
        cover_file_found = True

    if not cover_file_found:
        try:
            # debug_print("i",
            #     f"Downloading {key + source_cover_ext}.",
            # )
            try:
                cover = f"https://img.youtube.com/vi/{key}/maxresdefault.jpg"
                urlretrieve(cover, path.join(temp_path, f"{key + source_cover_ext}"))
                # debug_print("i",
                #     f"Successfully downloaded {key + source_cover_ext}.",
                # )

            # caused mostly by files generated from non-youtube music id's
            # but this is an inconsistent error, it can happen to youtube music files too, have no idea as to why
            # here's hoping the fallback to always work
            except HTTPError:
                # try:
                cover = f"https://img.youtube.com/vi/{key}/hqdefault.jpg"
                urlretrieve(cover, path.join(temp_path, f"{key + source_cover_ext}"))
                # debug_print("i",
                #     f"Successfully downloaded {key + source_cover_ext}.",
                # )
                # except HTTPError:
                #     exception = HTTPError.reason
                #     # debug_print("e",
                #         f"Couldn't download {key + source_cover_ext}, skipping download.",
                #         error_type="JustYoutubeThings",
                #     )
                #     print(exception)
                #     return 1, exception

            # TODO find out a way to log images that are actually 16:9 (i.e files generated from non-youtube music id's)
            img = Image.open(path.join(temp_path, key + source_cover_ext))
            width, height = img.size
            if width % 16 == 0 and height % 9 == 0:
                area_to_be_cut = (width - height) / 2
                cropped_img = img.crop(
                    (area_to_be_cut, 0, width - area_to_be_cut, height)
                )
                cropped_img.save(path.join(temp_path, key + source_cover_ext))
                # debug_print("i",
                #     f"Successfully cropped {key + source_cover_ext}.",
                # )

        except FileExistsError:
            pass
            # debug_print("i",
            #     f"{key + source_cover_ext} already exists, skipping download.",
            #     error_type="FileExistsError",
            # )

    try:
        if not audio_file_found:
            # debug_print("i",
            #     f"Moving audio file to {download_path}.",
            # )
            rename(
                path.join(temp_path, download_filename + download_ext),
                path.join(download_path, key + download_ext),
            )

    except FileExistsError:
        remove(path.join(temp_path, download_filename + download_ext))
        # debug_print("w",
        #     f"{key + download_ext} already exists!",
        #     error_type="FileExistsError",
        # )

    except FileNotFoundError:
        pass
        # debug_print("w",
        #     f"{key + download_ext} doesn't exist!",
        #     error_type="FileNotFoundError",
        # )

    except PermissionError:
        pass
        # debug_print("e",
        #     f"{key + download_ext} is in use!",
        #     error_type="PermissionError",
        # )
        # TODO wait a little then retry?

    try:
        if not cover_file_found:
            # debug_print("i",
            #     f"Moving cover file to {download_path}.",
            # )
            rename(
                path.join(temp_path, key + source_cover_ext),
                path.join(download_path, key + source_cover_ext),
            )

            # debug_print("i",
            #     f"Successfully moved files to {download_path}.",
            # )

        return 0, 0

    except FileExistsError:
        remove(path.join(temp_path, key + source_cover_ext))
        # debug_print("w",
        #     f"{key + source_cover_ext} file already exists!",
        #     error_type="FileExistsError",
        # )

    except FileNotFoundError:
        pass
        # debug_print("w",
        #     f"{key + source_cover_ext} file doesn't exist!",
        #     error_type="FileNotFoundError",
        # )

    except PermissionError:
        pass
        # debug_print("e",
        #     f"{key + source_cover_ext} is in use!",
        #     error_type="PermissionError",
        # )
        # TODO wait a little then retry?
