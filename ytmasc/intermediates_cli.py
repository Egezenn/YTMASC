"Provides chained functions for CLI"

from argparse import ArgumentParser
from inspect import currentframe

from .intermediates import update_library_with_manual_changes_on_files, run_tasks
from .tk_gui import create_gui
from .parser import parse_library_page, parse_ri_music_db
from .utility import (
    convert_csv_to_json,
    convert_json_to_csv,
    csv_library_data_path,
    get_current_function,
    library_data_path,
    read_txt,
    read_yaml,
    update_yaml,
    yaml_config,
)


def get_cli_args():
    parser = ArgumentParser()
    # entry point
    parser.add_argument("positional_arg", nargs="?", type=str, help="gui|run|set")

    # yaml config settings
    parser.add_argument(
        "setting_category", nargs="?", type=str, help="parser | fetcherArgs | tasks"
    )  # could just not make a category check, values are unique
    parser.add_argument(
        "setting",
        nargs="?",
        type=str,
        help="parse_ri_music_db, parse_library_page, run_fetcher, delete_library_page_files_afterwards | resendAmount, inbetweenDelay, dialogWaitDelay, openingDelay, closingDelay, savePageAsIndexOnRightClick | download, convert, tag",
    )
    parser.add_argument(
        "setting_value",
        nargs="?",
        type=str,
        help="parser -> inbetweenDelay, dialogWaitDelay == float, else == boolean | byte",
    )

    # add these to entry point rather than an option? they're not really configuring anything but rather are utility
    parser.add_argument(
        "--update_library_with_manual_changes_on_files", action="store_true", help=""
    )
    parser.add_argument("--export_library_as_csv", action="store_true", help="")
    parser.add_argument("--import_csv_to_library", action="store_true", help="")
    parser.add_argument("--update_tags", action="store_true", help="")

    return parser.parse_args()


def handle_cli(args: classmethod):
    # launch gui
    if args.positional_arg == "gui" or args.positional_arg == "g":
        create_gui()

    # run according to the configuration
    elif args.positional_arg == "run" or args.positional_arg == "r":
        handle_run(args)

    # show settings if index 2 is empty or invalid, otherwise set values
    elif args.positional_arg == "set" or args.positional_arg == "s":
        handle_settings(args)

    elif args.update_library_with_manual_changes_on_files:
        update_library_with_manual_changes_on_files()

    elif args.export_library_as_csv:
        convert_json_to_csv(library_data_path, csv_library_data_path)

    elif args.import_csv_to_library:
        convert_csv_to_json(csv_library_data_path, library_data_path)
        # should work properly now with fillna()

    elif args.update_tags:
        pass

    else:
        print(
            "no args given, type -h to see what is available"
        )  # replace this later on


def handle_settings(args):
    "Handles user input for configuring the config.yaml"
    config = read_yaml(yaml_config)

    if args.setting_category == None:
        print(read_txt(yaml_config))

    for setting_category in config:
        if (
            args.setting_category == setting_category
        ):  # could just not make a category check, values are unique
            for setting in config[setting_category]:
                if args.setting == setting:
                    args.setting_value = (
                        float(args.setting_value)
                        if "." in args.setting_value
                        else int(args.setting_value)
                    )
                    config[args.setting_category][args.setting] = args.setting_value
                    break
            break
    update_yaml(yaml_config, config)


def handle_run(args):
    current_function = get_current_function(currentframe())
    config = read_yaml(yaml_config)
    if config["parser"]["parse_library_page"]:
        parse_library_page(
            config["parser"]["run_fetcher"],
            [
                config["fetcherArgs"]["resendAmount"],
                config["fetcherArgs"]["inbetweenDelay"],
                config["fetcherArgs"]["dialogWaitDelay"],
                config["fetcherArgs"]["openingDelay"],
                config["fetcherArgs"]["closingDelay"],
                config["fetcherArgs"]["savePageAsIndexOnRightClick"],
            ],
            config["parser"]["delete_library_page_files_afterwards"],
        )

    if config["parser"]["parse_ri_music_db"]:
        parse_ri_music_db()

    run_tasks(
        config["tasks"]["download"], config["tasks"]["convert"], config["tasks"]["tag"]
    )
