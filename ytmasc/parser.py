import logging
import os
import sqlite3
import time

import bs4

from ytmasc.fetcher import fetch_lib_page
from ytmasc.intermediates import check_if_data_exists, delete_library_page_files, find_newest_ri_music_export
from ytmasc.utility import library_data, library_data_path, library_page, library_page_path, sort_nested, update_json

logger = logging.getLogger(__name__)


def parse_library_page(run_fetcher: bool, fetcher_params: list, delete_library_page_files_afterwards: bool):

    if run_fetcher:
        delete_library_page_files(True)

        logger.info("Running fetcer..")
        fetch_lib_page(*fetcher_params)

        while not os.path.isfile(library_page_path):
            time.sleep(1)
        logger.info(f"{library_page} is found")
        time.sleep(5)

    if check_if_data_exists("library"):
        with open(library_page_path, encoding="utf-8") as file:
            soup = bs4.BeautifulSoup(file, "html.parser")

            base_selector = "ytmusic-responsive-list-item-renderer.style-scope.ytmusic-playlist-shelf-renderer"
            logger.info(f"Parsing {library_page}..")
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
                        logger.warning(
                            f"YouTube didn't fail to provide another edge case, watch_id {title_element['href'][34:-8]} by \"{artist_element.text}\"'s title is {title_element.text}."
                        )

            else:
                logger.error("Page is corrupted.")

            logger.info(f"Successfully parsed {library_page}.")
            update_json(library_data_path, sort_nested(json))

            if delete_library_page_files_afterwards:
                delete_library_page_files(delete_library_page_files_afterwards)

    else:
        logger.error(f"{library_page} doesn't exist, use fetcher to get one.")
        pass


def parse_ri_music_db():
    if check_if_data_exists("export_ri"):
        database = find_newest_ri_music_export()
        logger.info(f"RiMusic export ({database}) found, parsing it..")
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        cursor.execute("SELECT id, title, artistsText, likedAt FROM Song WHERE likedAt IS NOT NULL")
        rows = cursor.fetchall()

        json = {}
        for row in rows:
            song_id, title, artists, liked_at = row
            json[song_id] = {
                "artist": artists,
                "title": title,
            }

        cursor.close()
        connection.close()

        update_json(library_data_path, sort_nested(json))

        logger.info(f"Successfully parsed RiMusic export and updated {library_data}.")

    else:
        logger.warning("No RiMusic export found.")
        pass
