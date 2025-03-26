import click

from ytmasc.utility import setup_logging


@click.command(context_settings=dict(help_option_names=["-h", "--help"], max_content_width=120))
@click.option("--verbosity", type=click.Choice(["d", "i", "w", "e", "c"]), default="w", help="Log verbosity")
# START of Library_operations
@click.option("--import-path", type=str, multiple=True, help="Path to your file")
# .csv, .db, .json
# get extension from the string, raise error if unsupported
@click.option(
    "--import-level", type=click.Choice(["soft", "soft-no-overwrite", "hard"]), default="soft", help="Import level"
)  # ignore if --import is not passed in
@click.option("--export", type=click.Choice(["csv", "json"]), default="csv", help="Whether to export")
@click.option(
    "--parse-library-page",
    type=click.Choice(["fetch", "no-fetch"]),
    help="Whether to parse the library page & option to run fetcher",
)
@click.option("--delete-library-page-files-afterwards", is_flag=True, default=False, help="Delete library page files")
@click.option(
    "--update-library-with-manual-changes-on-files",
    is_flag=True,
    default=False,
    help="Update the library with changes in songs",
)
@click.option("--refetch-metadata", is_flag=True, default=False, help="Fetches & overwrites metadata")
# START of Tasks
@click.option("--download", is_flag=True, default=False, help="Whether to download files")
@click.option("--convert", type=click.Choice(["mp3", "m4a"]), default="mp3", help="Whether to convert files")
@click.option("--tag", is_flag=True, default=False, help="Whether to tag files")
# START of Library_tools
@click.option(
    "--lib-tool",
    type=click.Choice(["lib-compare", "lib-find-same", "lib-find-unpaired", "lib-replace-fails"]),
    multiple=True,
    help="Which library utility to run",
)
# Fetcher args
@click.option("--resend-amount", type=int, default=60, help="[FETCHER] Amount of END to send")
@click.option("--inbetween-delay", type=float, default=0.2, help="[FETCHER] Delay inbetween END's")
@click.option("--dialog-wait-delay", type=float, default=0.5, help="[FETCHER] Delay for the dialogs to show up")
@click.option("--opening-delay", type=int, default=6, help="[FETCHER] Delay for the page to initialize")
@click.option("--closing-delay", type=int, default=3, help="[FETCHER] Delay for the page to download fully")
@click.option(
    "--save-page-as-index-on-right-click", type=int, default=5, help='[FETCHER] Index of "Save page as" in menu'
)
def cli(
    verbosity,
    import_path,
    import_type,
    export,
    parse_library_page,
    delete_library_page_files_afterwards,
    update_library_with_manual_changes_on_files,
    refetch_metadata,
    download,
    convert,
    tag,
    lib_tool,
    resend_amount,
    inbetween_delay,
    dialog_wait_delay,
    opening_delay,
    closing_delay,
    save_page_as_index_on_right_click,
):
    setup_logging(verbosity)


if __name__ == "__main__":
    cli()
