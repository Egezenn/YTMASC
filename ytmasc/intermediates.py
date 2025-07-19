import logging
import os
import platform
import shutil
import sqlite3
import time
import webbrowser

import bs4
import pandas
import pyautogui
import pygetwindow

from ytmasc.tasks import Tasks
from ytmasc.utility import (
    audio_conversion_ext,
    current_path,
    get_file_extension,
    get_filename,
    library_data_path,
    library_page_path,
    read_json,
    update_library_for_watch_id,
    write_json,
)

logger = logging.getLogger(__name__)


def delete_library_page_files(fetcher_is_going_to_run=False):
    try:
        os.remove(library_page_path)
        # TODO check function get_filename
        shutil.rmtree(f"{get_filename(library_page_path)}_files")

    except FileNotFoundError:
        if fetcher_is_going_to_run:
            pass


def run_tasks(download: bool, convert: bool, tag: bool):
    json = read_json(library_data_path)

    if download:
        Tasks.download_bulk(json)

    if convert:
        Tasks.convert_bulk(json)

    if tag:
        Tasks.tag_bulk(json)


def import_operations(args: list[str], overwrite=True):
    # TODO Metrolist exports, check if method for Kreate which got forked from RiMusic still works
    json_data = read_json(library_data_path)

    for arg in args:
        if arg == "files":
            for watch_id in json_data:
                for ext in audio_conversion_ext:
                    try:
                        audio_file = mutagen.File(audio_file_path)
                    except Exception as e:
                        print(str(e))

                    if audio_file.mime[0] == "audio/mpeg":
                        artist_frame = audio_file.tags.get("TPE1")
                        title_frame = audio_file.tags.get("TIT2")
                        artist = artist.text[0] if artist_frame else ""
                        title = title.text[0] if title_frame else ""

                    elif audio_file.mime[0] == "audio/opus":
                        artist = audio_file.tags.get("artist", [None])[0]
                        title = audio_file.tags.get("title", [None])[0]
                        print(artist, title)
                    else:
                        raise Exception

                json_data = update_library_for_watch_id(json_data, watch_id, artist_text, title_text, overwrite)

            write_json(library_data_path, json_data)

        elif os.path.isfile(arg):
            ext = get_file_extension(arg)

            if ext == "csv":
                df = pandas.read_csv(arg)
                df.fillna("", inplace=True)

                for _, row in df.iterrows():
                    watch_id = row.iloc[0]
                    artist = row.iloc[1]
                    title = row.iloc[2]

                    json_data = update_library_for_watch_id(json_data, watch_id, artist, title, overwrite)

                write_json(library_data_path, json_data)

            elif ext == ".db":
                connection = sqlite3.connect(arg)
                cursor = connection.cursor()

                cursor.execute("SELECT id, title, artistsText, likedAt FROM Song WHERE likedAt IS NOT NULL")
                rows = cursor.fetchall()
                cursor.close()
                connection.close()

                for row in rows:
                    watch_id, title, artist, liked_at = row

                    json_data = update_library_for_watch_id(json_data, watch_id, artist, title, overwrite)

                write_json(library_data_path, json_data)


def import_library_page(
    run_fetcher: bool, fetcher_params: list, delete_library_page_files_afterwards: bool, overwrite: False
):
    if run_fetcher:
        delete_library_page_files(True)

        fetch_lib_page(*fetcher_params)

        while not os.path.isfile(library_page_path):
            time.sleep(1)
        time.sleep(5)

    if os.path.exists(library_page_path):
        with open(library_page_path, encoding="utf-8") as file:
            json_data = read_json(library_data_path)

            soup = bs4.BeautifulSoup(file, "html.parser")

            base_selector = "ytmusic-responsive-list-item-renderer.style-scope.ytmusic-playlist-shelf-renderer"
            base_elements = soup.select(base_selector)

            data = {}
            if base_elements:
                for element in base_elements:
                    title_element = element.select_one(
                        "div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a:nth-of-type(1).yt-simple-endpoint.style-scope.yt-formatted-string:nth-of-type(1)"
                    )
                    artist_element = element.select_one(
                        "div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.secondary-flex-columns.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string:nth-child(1).flex-column.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string"
                    )
                    # TODO make use of this, throw Albumless-<index> if it's null for compatibility with players where they make albumless songs into one album.
                    # album_element = element.select_one(
                    #     "div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.secondary-flex-columns.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string:nth-child(2).flex-column.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string"
                    # )

                    if title_element.text != "Video":  # youtube things
                        # if album_element:
                        #     data[title_element["href"][34:-8]] = {
                        #         "artist": artist_element.text,
                        #         "title": title_element.text,
                        #         "album": album_element.text,
                        #     }
                        # else:

                        update_library_for_watch_id(
                            json_data,
                            data[title_element["href"][34:-8]],
                            artist_element.text,
                            title_element.text,
                            overwrite,
                        )
                        data[title_element["href"][34:-8]] = {
                            "artist": artist_element.text,
                            "title": title_element.text,
                        }

            if delete_library_page_files_afterwards:
                delete_library_page_files()


def fetch_lib_page(
    resend_amount=60,
    inbetween_delay=0.2,
    dialog_wait_delay=0.5,
    opening_delay=6,
    closing_delay=3,
    save_page_as_index_on_right_click=5,
):
    systemInfo = platform.system()
    if systemInfo == "Windows":
        # initializing the browser
        webbrowser.open_new_tab("https://music.youtube.com/playlist?list=LM")
        pyautogui.sleep(opening_delay)

        # scrolling the page down and getting to save dialog
        for _ in range(resend_amount):
            pyautogui.press(["end"])
            pyautogui.sleep(inbetween_delay)
        pyautogui.press("apps")
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.press(["down"] * save_page_as_index_on_right_click, interval=0.1)
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.press("enter")
        pyautogui.sleep(dialog_wait_delay)

        # saving the files and exiting the browser
        pygetwindow.getWindowsWithTitle("Save As")[0].activate()
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.typewrite(os.path.join(current_path, library_page_path))
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.press("enter")
        pyautogui.sleep(closing_delay)
        pyautogui.hotkey("ctrl", "w")
        pyautogui.sleep(dialog_wait_delay)
