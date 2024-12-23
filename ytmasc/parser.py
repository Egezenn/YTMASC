"Provides parsing functions for library page and RiMusic exports."
from logging import getLogger
from os import path
from sqlite3 import connect
from time import sleep

from bs4 import BeautifulSoup

from ytmasc.fetcher import fetch
from ytmasc.intermediates import delete_library_page_files, find_newest_ri_music_export
from ytmasc.utility import (
    library_data_path,
    library_page,
    library_page_path,
    sort_dictionary_based_on_value_inside_nested_dictionary,
    update_json,
)

logger = getLogger(__name__)


def parse_library_page(
    run_fetcher: bool, fetcher_params: list, delete_library_page_files_afterwards: bool
):

    if run_fetcher:
        delete_library_page_files(True)

        logger.info("Running fetcer..")
        fetch(*fetcher_params)

        while not path.isfile(library_page_path):
            sleep(1)

        logger.info(f"{library_page} is found")

        sleep(5)

    if path.isfile(library_page_path):
        with open(library_page_path, encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

            base_selector = "ytmusic-responsive-list-item-renderer.style-scope.ytmusic-playlist-shelf-renderer"

            logger.info(f"Parsing {library_page}..")

            base_elements = soup.select(base_selector)

            json = {}
            if base_elements:
                for element in base_elements:
                    title_element = element.select_one(
                        "div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a:nth-of-type(1).yt-simple-endpoint.style-scope.yt-formatted-string"
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
                            f"YouTube didn't fail to provide another edge case, ID {title_element['href'][34:-8]} by \"{artist_element.text}\"'s title is {title_element.text}"
                        )

            else:
                logger.error("Page is corrupted")

            logger.info(f"Successfully parsed {library_page}.")

        json = sort_dictionary_based_on_value_inside_nested_dictionary(json)
        update_json(library_data_path, json)

        if delete_library_page_files_afterwards:
            delete_library_page_files(delete_library_page_files_afterwards)

    else:
        logger.error(f"{library_page} doesn't exist, use fetcher to get one.")
        pass


def parse_ri_music_db():
    database = find_newest_ri_music_export()
    connection = connect(database)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, artistsText, likedAt FROM Song WHERE likedAt IS NOT NULL"
    )
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

    sort_dictionary_based_on_value_inside_nested_dictionary(json)
    update_json(library_data_path, json)
