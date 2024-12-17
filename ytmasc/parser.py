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

            title_selector = "ytmusic-responsive-list-item-renderer.style-scope.ytmusic-playlist-shelf-renderer > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a:nth-of-type(1).yt-simple-endpoint.style-scope.yt-formatted-string"
            artist_selector = "ytmusic-responsive-list-item-renderer.style-scope.ytmusic-playlist-shelf-renderer > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.secondary-flex-columns.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string:nth-child(2n+1).flex-column.style-scope.ytmusic-responsive-list-item-renderer"
            # album_selector = "ytmusic-responsive-list-item-renderer.style-scope.ytmusic-playlist-shelf-renderer > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.secondary-flex-columns.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string:nth-child(2n).flex-column.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a:nth-of-type(1).yt-simple-endpoint.style-scope.yt-formatted-string"

            logger.info(f"Parsing {library_page}..")

            title_elements = soup.select(title_selector)
            artist_elements = soup.select(artist_selector)
            # this is a little problematic to include as they might not belong to an album, have to iterate through each div and see if it has an album or not
            # album_elements = soup.select(album_selector)

            json = {}

            for n in range(len(title_elements)):
                json[title_elements[n]["href"][34:-8]] = {
                    "artist": f"{artist_elements[n]['title']}",
                    "title": f"{title_elements[n].text}",
                }

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
