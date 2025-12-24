import concurrent.futures
import logging
from pathlib import Path
import queue

import rich_click as click

from . import converter
from . import core
from . import downloader
from . import tagger
from . import utils

# Rich Click Configuration
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True
click.rich_click.STYLE_OPTIONS_PANEL_BORDER = "none"
click.rich_click.STYLE_OPTIONS_TABLE_BOX = None
click.rich_click.STYLE_OPTIONS_PANEL_BOX = None
click.rich_click.STYLE_COMMANDS_TABLE_BOX = None
click.rich_click.STYLE_COMMANDS_PANEL_BOX = None

click.rich_click.OPTION_GROUPS = {
    "ytmasc run": [
        {"name": "Metadata Options", "options": ["--tag-albums", "--force-metadata", "--db"]},
        {"name": "Processing Options", "options": ["--start-index", "--workers"]},
        {
            "name": "File Options",
            "options": [
                "--working-dir",
                "--format",
                "--keep-source",
                "--download-extras",
                "--embed-extras",
                "--delete-embeds",
            ],
        },
    ],
    "ytmasc download": [
        {"name": "Download Options", "options": ["--download-extras"]},
        {"name": "File Options", "options": ["--working-dir"]},
    ],
    "ytmasc convert": [
        {"name": "Conversion Options", "options": ["--format", "--keep-source"]},
        {"name": "File Options", "options": ["--working-dir"]},
    ],
    "ytmasc tag": [
        {"name": "Metadata Options", "options": ["--artist", "--title", "--album", "--tag-album", "--db", "--lock"]},
        {"name": "File Options", "options": ["--working-dir", "--embed-extras", "--delete-embeds"]},
    ],
}


# Setup logging
utils.setup_logging()
logger = logging.getLogger(__name__)


try:
    from importlib.metadata import version, PackageNotFoundError

    __version__ = version("ytmasc")
except (ImportError, PackageNotFoundError):
    __version__ = "unknown"


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "-v", "--version")
def cli():
    """YTMASC: YouTube Music Audio Scraper & Synchronizer"""
    utils.check_dependencies()


@cli.command()
@click.option(
    "--db",
    default=utils.LIBRARY_FILE,
    type=click.Path(exists=False),
    help="Path to library JSON",
)
@click.option(
    "--start-index",
    default=1,
    type=int,
    help="Start processing from this index (1-based).",
)
@click.option(
    "--workers",
    default=3,
    type=int,
    help="Number of worker threads to use.",
)
@click.option(
    "--keep-source",
    is_flag=True,
    help="Keep source files after conversion.",
)
@click.option("--format", "-f", default="opus", help="Target format (opus*/mp3)")
@click.option(
    "--download-extras",
    default="cover,lyric",
    help="Comma-separated extras to download (cover*, lyric*).",
)
@click.option(
    "--embed-extras",
    default="cover",
    help="Comma-separated extras to embed (cover*, lyric).",
)
@click.option(
    "--delete-embeds",
    is_flag=True,
    help="Delete source lyrics/cover files after embedding into audio.",
)
@click.option(
    "--tag-albums",
    is_flag=True,
    help="Use album metadata from library for tagging (falls back to sequential index if missing).",
)
@click.option(
    "--force-metadata",
    is_flag=True,
    help="Force metadata update from YouTube Music (respects lock).",
)
@click.option("--working-dir", "--work", "-w", type=click.Path(path_type=Path), help="Directory to save downloads.")
def run(
    db,
    start_index,
    workers,
    keep_source,
    format,
    download_extras,
    embed_extras,
    delete_embeds,
    tag_albums,
    force_metadata,
    working_dir,
):
    """Process the entire library from the database."""
    parsed_download_extras = utils.parse_extras(download_extras)
    parsed_embed_extras = utils.parse_extras(embed_extras)
    db_path = Path(db)
    if not db_path.exists():
        logger.info(f"Database not found at {db_path}")
        return

    db_obj = core.Database(db_path)

    # Sort items by title for album ordering
    items = []
    for watch_id, meta in db_obj.items():
        title = meta.get("title", "")
        items.append((watch_id, meta, title))

    total = len(items)
    logger.info(f"Processing {total} items from {db_path}...")

    # Calculate padding width based on total items
    padding = len(str(total))

    # Pre-calculate album tags so we can pass them to threads
    album_tags = {}
    no_album_count = 0
    no_album_padding = 0
    if tag_albums:
        no_album_count = sum(1 for _, meta, _ in items if not meta.get("album"))
        no_album_padding = len(str(no_album_count))

    no_album_counter = 0

    processed_items = []

    for i, (watch_id, meta, *_) in enumerate(items, 1):
        # Calculate album tag
        album_tag = str(i).zfill(padding)
        if tag_albums:
            if meta.get("album"):
                album_tag = meta["album"]
            else:
                no_album_counter += 1
                album_tag = str(no_album_counter).zfill(no_album_padding)

        album_tags[watch_id] = album_tag

        # Prepare item for processing if within range
        if i >= start_index:
            processed_items.append((i, (watch_id, meta, meta.get("title"))))

    # Prepare options dict to pass to workers
    options = {
        "keep_source": keep_source,
        "format": format,
        "download_extras": parsed_download_extras,
        "delete_embeds": delete_embeds,
        "embed_extras": parsed_embed_extras,
        "force_metadata": force_metadata,
        "tag_albums": tag_albums,
        "total": total,
        "album_tags": album_tags,
    }

    # Worker queue setup
    worker_queue = queue.Queue()
    for i in range(1, workers + 1):
        worker_queue.put(i)

    if working_dir:
        working_dir.mkdir(parents=True, exist_ok=True)
    else:
        working_dir = utils.WORKING_DIR

    dl = downloader.Downloader(working_dir=working_dir, download_extras=parsed_download_extras)
    cv = converter.Converter(working_dir=working_dir)
    tg = tagger.Tagger(working_dir=working_dir)

    worker_padding = len(str(workers))

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers, initializer=core.pool_initializer, initargs=(worker_queue, worker_padding)
    ) as executor:

        futures = {executor.submit(core.process_item, item, options, dl, cv, tg): item for item in processed_items}

        count = 0
        try:
            for future in concurrent.futures.as_completed(futures):
                try:
                    watch_id, updated_meta, success = future.result()

                    if updated_meta:
                        # Update database in main thread
                        # We use save_to_disk=False for batch updates
                        db_obj.update(watch_id, updated_meta, save_to_disk=False)

                    count += 1
                    # periodically save
                    if count % 10 == 0:
                        db_obj.save()

                except Exception as e:
                    logger.error(f"Worker failed: {e}")

        except KeyboardInterrupt:
            logger.info("Interrupted, shutting down workers...")
            executor.shutdown(wait=False, cancel_futures=True)
            raise

    # Final save
    db_obj.save()
    logger.info("Done.")


@cli.command()
@click.argument("watch_id")
@click.option(
    "--download-extras",
    default="cover,lyric",
    help="Comma-separated extras to download (cover*, lyric*).",
)
@click.option("--working-dir", "--work", "-w", type=click.Path(path_type=Path), help="Directory to save downloads.")
def download(watch_id, download_extras, working_dir):
    """Download a single video by Watch ID."""
    extras = utils.parse_extras(download_extras)
    if working_dir:
        working_dir.mkdir(parents=True, exist_ok=True)
    else:
        working_dir = utils.WORKING_DIR

    dl = downloader.Downloader(working_dir=working_dir, download_extras=extras)
    if dl.download(watch_id):
        logger.info(f"Downloaded {watch_id}")
    else:
        logger.info(f"Failed to download {watch_id}")


@cli.command()
@click.argument("watch_id")
@click.option(
    "--keep-source",
    is_flag=True,
    help="Keep source files after conversion.",
)
@click.option("--format", "-f", default="opus", help="Target format (opus*/mp3)")
@click.option(
    "--working-dir", "--work", "-w", type=click.Path(path_type=Path), help="Directory where files are located."
)
def convert(watch_id, keep_source, format, working_dir):
    """Convert a downloaded video."""
    if working_dir:
        if not working_dir.exists():
            logger.error(f"Directory {working_dir} does not exist.")
            return
    else:
        working_dir = utils.WORKING_DIR

    cv = converter.Converter(working_dir=working_dir)

    success_audio = cv.convert_audio(watch_id, format, keep_source=keep_source)
    success_image = cv.convert_image(watch_id, keep_source=keep_source)

    if success_audio:
        logger.info(f"Converted audio for {watch_id} to {format}")
    else:
        logger.info(f"Failed to convert audio for {watch_id}")

    if success_image:
        logger.info(f"Converted image for {watch_id}")
    else:
        logger.info(f"Failed to convert image for {watch_id} (or no image found)")


@cli.command()
@click.argument("watch_id")
@click.option("--artist", help="Artist name")
@click.option("--title", help="Track title")
@click.option(
    "--embed-extras",
    default="cover",
    help="Comma-separated extras to embed (cover*, lyric).",
)
@click.option(
    "--delete-embeds",
    is_flag=True,
    help="Delete source lyrics/cover files after embedding into audio.",
)
@click.option(
    "--working-dir", "--work", "-w", type=click.Path(path_type=Path), help="Directory where files are located."
)
@click.option(
    "--db",
    default=utils.LIBRARY_FILE,
    type=click.Path(path_type=Path),
    help="Path to library JSON",
)
@click.option("--lock", "-l", is_flag=True, help="Lock metadata in library.")
@click.option("--album", help="Album name")
@click.option("--tag-album", is_flag=True, help="Tag album from metadata.")
def tag(watch_id, artist, title, embed_extras, delete_embeds, working_dir, db, lock, album, tag_album):
    """Tag a file."""
    extras = utils.parse_extras(embed_extras)
    if working_dir:
        if not working_dir.exists():
            logger.error(f"Directory {working_dir} does not exist.")
            return
    else:
        working_dir = utils.WORKING_DIR

    # Initialize Database
    db_obj = core.Database(db)
    current_meta = db_obj.get(watch_id) or {}

    updates_made = False

    # 1. Update from Manual Args
    if artist:
        current_meta["artist"] = artist
        updates_made = True
    if title:
        current_meta["title"] = title
        updates_made = True
    if album:
        current_meta["album"] = album
        updates_made = True
    if lock:
        current_meta["lock"] = True
        updates_made = True

    # 2. Check if we still need metadata
    final_artist = current_meta.get("artist")
    final_title = current_meta.get("title")

    if not final_artist or not final_title:
        logger.info(f"Metadata missing for {watch_id}. Checking YouTube...")
        # Need downloader to fetch metadata
        dl = downloader.Downloader(working_dir=working_dir)
        fetched = dl.fetch_metadata(watch_id)

        if fetched:
            if not final_artist and fetched.get("artist"):
                final_artist = fetched["artist"]
                current_meta["artist"] = final_artist
                updates_made = True

            if not final_title and fetched.get("title"):
                final_title = fetched["title"]
                current_meta["title"] = final_title
                updates_made = True

            # Also opportunity to get album if missing
            if fetched.get("album"):
                if tag_album and "album" not in current_meta:
                    current_meta["album"] = fetched["album"]
                    updates_made = True
        else:
            logger.warning(f"Could not fetch metadata for {watch_id}")

    # Save updates if any
    if updates_made:
        db_obj.update(watch_id, current_meta)

    # Final fallbacks for display/tagging
    display_artist = final_artist if final_artist else "Unknown"
    display_title = final_title if final_title else "Unknown"

    # Determine album to tag
    tag_album_value = None
    if album:
        tag_album_value = album
    elif tag_album:
        tag_album_value = current_meta.get("album")

    tg = tagger.Tagger(working_dir=working_dir)
    if tg.tag(
        watch_id,
        display_artist,
        display_title,
        album=tag_album_value,
        embed_extras=extras,
        delete_embeds=delete_embeds,
    ):
        logger.info(f"Tagged {watch_id}")
    else:
        logger.info(f"Failed to tag {watch_id}")


if __name__ == "__main__":
    cli()
