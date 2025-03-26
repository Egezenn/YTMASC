import logging
import os
import sqlite3
import time

import bs4

from ytmasc.fetcher import fetch_lib_page
from ytmasc.intermediates import delete_library_page_files, update_library_for_watch_id
from ytmasc.utility import library_data_path, library_page, library_page_path, sort_nested, update_json

logger = logging.getLogger(__name__)


def parse_library_page(run_fetcher: bool, fetcher_params: list, delete_library_page_files_afterwards: bool):

    if run_fetcher:
        delete_library_page_files(True)

        fetch_lib_page(*fetcher_params)

        while not os.path.isfile(library_page_path):
            time.sleep(1)
        time.sleep(5)

    if os.path.exists(library_page_path):
        with open(library_page_path, encoding="utf-8") as file:
            soup = bs4.BeautifulSoup(file, "html.parser")

            base_selector = "ytmusic-responsive-list-item-renderer.style-scope.ytmusic-playlist-shelf-renderer"
            base_elements = soup.select(base_selector)

            json = {}
            if base_elements:
                for element in base_elements:
                    title_element = element.select_one(
                        "div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a:nth-of-type(1).yt-simple-endpoint.style-scope.yt-formatted-string:nth-of-type(1)"
                    )
                    artist_element = element.select_one(
                        "div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.secondary-flex-columns.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string:nth-child(1).flex-column.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string"
                    )
                    # album_element = element.select_one(
                    #     "div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.secondary-flex-columns.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string:nth-child(2).flex-column.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string"
                    # )

                    if title_element.text != "Video":  # oh dear god
                        # if album_element:
                        #     json[title_element["href"][34:-8]] = {
                        #         "artist": artist_element.text,
                        #         "title": title_element.text,
                        #         "album": album_element.text,
                        #     }
                        # else:
                        json[title_element["href"][34:-8]] = {
                            "artist": artist_element.text,
                            "title": title_element.text,
                        }
                    else:
                        pass
            else:
                pass

            update_library_for_watch_id()

            if delete_library_page_files_afterwards:
                delete_library_page_files(delete_library_page_files_afterwards)

    else:
        pass
