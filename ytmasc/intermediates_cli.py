from argparse import ArgumentParser

from ytmasc.database_helpers import compare, find_unpaired_files, replace_fails
from ytmasc.intermediates import (
    import_csv,
    run_tasks,
    update_library_with_manual_changes_on_files,
)
from ytmasc.parser import parse_library_page, parse_ri_music_db
from ytmasc.tk_gui import create_gui
from ytmasc.utility import (
    convert_csv_to_json,
    convert_json_to_csv,
    csv_library_data_path,
    download_path,
    library_data_path,
    read_txt,
    read_yaml,
    update_yaml,
    yaml_config,
)


def get_cli_args():
    parser = ArgumentParser()
    parser.add_argument("positional_arg", nargs="?", type=str, help="gui|run|set")

    parser.add_argument(
        "setting",
        nargs="?",
        type=str,
        help="parse-ri-music-db, parse-library-page, run-fetcher, delete-library-page-files-afterwards | resend-amount, inbetween-delay, dialog-wait-delay, opening-delay, closing-delay, save-page-as-index-on-right-click | download, convert, tag",
    )
    parser.add_argument(
        "setting_value",
        nargs="?",
        type=str,
        help="parser -> inbetween-delay, dialog-wait-delay == float, else == boolean | byte",
    )

    parser.add_argument(
        "--update-library-with-manual-changes-on-files",
        action="store_true",
        help="Updates library with tag changes you've made to the files",
    )
    parser.add_argument(
        "--export-library-as-csv",
        action="store_true",
        help="Exports the library as a CSV file",
    )
    parser.add_argument(
        "--import-csv-to-library",
        action="store_true",
        help="Imports a CSV of 3 columns [ID, artist, title]. If keys exist but their values are different they will be updated with the tags from the CSV",
    )
    parser.add_argument(
        "--import-csv-to-library-no-overwrite",
        action="store_true",
        help="Imports a CSV of 3 columns [ID, artist, title]. If keys exist but their values are different they will NOT be updated with the tags from the CSV",
    )
    parser.add_argument(
        "--direct-import", action="store_true", help="Completely overwrites the library"
    )
    parser.add_argument(
        "--db-compare",
        action="store_true",
        help="Helps you migrate your old library by checking if any of them exist in your current library to avoid duplication",
    )
    parser.add_argument(
        "--db-find-unpaired", action="store_true", help="Find unpaired items"
    )
    parser.add_argument(
        "--db-replace-fails",
        action="store_true",
        help="Helps you select a new file for the failed items.",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        default="w",
        action="store",
        help="Set the log verbosity d | i | w | e | c",
    )

    return parser.parse_args(), parser


def handle_cli(args: classmethod, parser: classmethod):
    if args.positional_arg == "gui" or args.positional_arg == "g":
        create_gui()

    elif args.positional_arg == "run" or args.positional_arg == "r":
        handle_run()

    elif args.positional_arg == "set" or args.positional_arg == "s":
        handle_settings(args)

    else:
        parser.print_help()

    if args.update_library_with_manual_changes_on_files:
        update_library_with_manual_changes_on_files()

    if args.export_library_as_csv:
        convert_json_to_csv(library_data_path, csv_library_data_path)

    # modify this later on and get a filename
    if args.import_csv_to_library:
        import_csv(csv_library_data_path, library_data_path)
    elif args.import_csv_to_library_no_overwrite:
        import_csv(csv_library_data_path, library_data_path, overwrite=False)

    if args.direct_import:
        convert_csv_to_json(csv_library_data_path, library_data_path)

    if args.db_compare:
        compare()

    if args.db_find_unpaired:
        find_unpaired_files(download_path)

    if args.db_replace_fails:
        replace_fails()


def handle_settings(args: classmethod):
    config = read_yaml(yaml_config)

    if args.setting == None:
        print(read_txt(yaml_config))

    for setting_category in config.keys():
        for setting in config[setting_category]:
            if args.setting == setting:
                args.setting_value = (
                    float(args.setting_value)
                    if "." in args.setting_value
                    else int(args.setting_value)
                )
                config[setting_category][args.setting] = args.setting_value
                break

    update_yaml(yaml_config, config)


def handle_run():
    config = read_yaml(yaml_config)
    if config["parser"]["parse-library-page"]:
        parse_library_page(
            config["parser"]["run_fetcher"],
            [
                config["fetcher-args"]["resend-amount"],
                config["fetcher-args"]["inbetween-dDelay"],
                config["fetcher-args"]["dialog-wait-delay"],
                config["fetcher-args"]["opening-delay"],
                config["fetcher-args"]["closing-delay"],
                config["fetcher-args"]["save-page-as-index-on-right-click"],
            ],
            config["parser"]["delete-library-page-files-afterwards"],
        )

    if config["parser"]["parse-ri-music-db"]:
        parse_ri_music_db()

    run_tasks(
        config["tasks"]["download"], config["tasks"]["convert"], config["tasks"]["tag"]
    )
