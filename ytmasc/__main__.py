import os
import sys

import click
import fire

from ytmasc import lib_tools, utility
from ytmasc.intermediates import import_library_page as _import_library_page
from ytmasc.intermediates import import_operations
from ytmasc.lib_tools import refetch_metadata as _refetch_metadata
from ytmasc.tasks import Tasks
from ytmasc.utility import (
    check_if_directories_exist_and_make_if_not,
    convert_json_to_csv,
    data_path,
    download_path,
    get_filename,
    library_data_path,
    setup_logging,
)


# TODO rename library modification options
@click.command(context_settings=dict(help_option_names=["-h", "--help"], max_content_width=120), no_args_is_help=True)
@click.option("--fire", is_flag=True, help="Use Fire CLI instead for singular operations")
@click.option(
    "--verbosity",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="WARNING",
    help="Log verbosity",
)
# START of Library_operations
@click.option("--import-from", type=str, multiple=True, help="Path to your file or to import any file changes `files`")
# .csv, .db, .json
# get extension from the string, raise error if unsupported
@click.option(
    "--import-level",
    type=click.Choice(["soft", "soft-no-overwrite"]),
    default="soft",
    help="Soft means overwrite any change, no-overwrite keeps the data even if it's different.",
)  # ignore if --import is not passed in
@click.option("--export-to", help="Export path")
@click.option(
    "--import-library-page",
    type=click.Choice(["fetch-soft", "fetch-soft-no-overwrite", "no-fetch-soft" "no-fetch-soft-no-overwrite"]),
    help="Whether to import the library page & option to run fetcher and specification of import level",
)
@click.option(
    "--delete-library-page-files-afterwards",
    is_flag=True,
    default=False,
    help="Delete library page files after it's contents are imported",
)
@click.option(
    "--refetch-metadata",
    is_flag=True,
    default=False,
    help="Fetches metadata from YouTube if there are any empty fields",
)  # an option to lock metadata
@click.option(
    "--force-refetch", is_flag=True, default=False, help="Forcefully fetches & overwrites all metadata from YouTube"
)
# START of Tasks
@click.option("--download", is_flag=True, default=False, help="Download all keys found in library")
@click.option("--continue-download", is_flag=True, default=False, help="Watch ID to continue from")
@click.option(
    "--convert", type=click.Choice(["opus", "mp3"]), default="opus", help="Convert all files to specified format"
)
@click.option("--tag", is_flag=True, default=False, help="Tag all files")
@click.option("--generate-m3u", type=str, help="Generate an M3U playlist")
# START of Library_tools
@click.option("--lib-compare", nargs=2, help="[WIP] Compares 2 directories lets you operate on files")
@click.option(
    "--lib-find-same", is_flag=True, default=False, help="[WIP] Compares all files in a directory to themselves fuzzily"
)
@click.option(
    "--lib-find-unpaired", is_flag=True, default=False, help="Find files that doesn't have an audio or image pair"
)
@click.option(
    "--lib-find-unpaired-del",
    type=click.Choice(["audio", "image"]),
    help="Find files that doesn't have an audio or image pair",
)
@click.option(
    "--lib-replace-fails", is_flag=True, default=False, help="[WIP] Find replacements for files that have failed"
)
# Fetcher args
@click.option("--resend-amount", type=int, default=60, help="[FETCHER] Amount of END key to send")
@click.option("--inbetween-delay", type=float, default=0.2, help="[FETCHER] Delay inbetween END key")
@click.option("--dialog-wait-delay", type=float, default=0.5, help="[FETCHER] Delay for the dialogs to show up")
@click.option("--opening-delay", type=int, default=6, help="[FETCHER] Delay for the page to initialize")
@click.option("--closing-delay", type=int, default=3, help="[FETCHER] Delay for the page to download fully")
@click.option(
    "--save-page-as-index-on-right-click", type=int, default=5, help='[FETCHER] Index of "Save page as" in menu'
)
def cli(
    fire,
    verbosity,
    import_from,
    import_level,
    export_to,
    import_library_page,
    delete_library_page_files_afterwards,
    refetch_metadata,
    force_refetch,
    download,
    continue_download,
    convert,
    tag,
    generate_m3u,
    lib_compare,
    lib_find_same,
    lib_find_unpaired,
    lib_find_unpaired_del,
    lib_replace_fails,
    resend_amount,
    inbetween_delay,
    dialog_wait_delay,
    opening_delay,
    closing_delay,
    save_page_as_index_on_right_click,
):
    check_if_directories_exist_and_make_if_not(download_path, data_path)
    setup_logging(verbosity)

    if import_library_page:
        fetch_state = (
            True if import_library_page == "fetch-soft-no-overwrite" or import_library_page == "fetch-soft" else False
        )
        overwrite_state_lib = (
            True if import_library_page == "fetch-soft" or import_library_page == "no-fetch-soft" else False
        )
        _import_library_page(
            fetch_state,
            [
                resend_amount,
                inbetween_delay,
                dialog_wait_delay,
                opening_delay,
                closing_delay,
                save_page_as_index_on_right_click,
            ],
            delete_library_page_files_afterwards,
            overwrite_state_lib,
        )

    if import_from:
        overwrite_state_file = False if import_level == "soft-no-overwrite" else True
        import_operations(import_from, overwrite_state_file)

    if refetch_metadata:
        _refetch_metadata(force=force_refetch)

    if export_to:
        convert_json_to_csv(library_data_path, export_to)

    if download:
        files = [
            os.path.join(utility.download_path, f)
            for f in os.listdir(utility.download_path)
            if os.path.isfile(os.path.join(utility.download_path, f))
        ]

        # TODO conversion will mess this up, retain creation dates or switch to modification?
        if continue_download and files:
            last_created_file = get_filename(max(files, key=os.path.getctime))
            Tasks.download_bulk(library_data_path, last_created_file)

        else:
            Tasks.download_bulk(library_data_path)

    if convert:
        Tasks.convert_bulk(library_data_path, convert)

    if tag:
        Tasks.tag_bulk(library_data_path)

    if generate_m3u:
        lib_tools.generate_playlist(generate_m3u)

    if lib_find_same:
        lib_tools.find_same_metadata()

    if lib_find_unpaired:
        if lib_find_unpaired_del:
            lib_tools.find_unpaired(lib_find_unpaired_del)
        else:
            lib_tools.find_unpaired()

    if lib_replace_fails:
        lib_tools.replace_fails()

    if lib_compare:
        lib_tools.compare()


if __name__ == "__main__":
    if "--fire" in sys.argv:
        check_if_directories_exist_and_make_if_not(download_path, data_path)
        sys.argv.remove("--fire")
        fire.Fire(Tasks)

    else:
        cli()
