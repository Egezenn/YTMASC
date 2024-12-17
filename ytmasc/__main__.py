"Handles all things regarding CLI arguments, launches UI"
import logging

from ytmasc.intermediates import create_config
from ytmasc.intermediates_cli import get_cli_args, handle_cli
from ytmasc.utility import (
    check_if_directories_exist_and_make_if_not,
    data_path,
    download_path,
    setup_logging,
    temp_path,
)

root_logger = logging.getLogger()

if __name__ == "__main__":
    check_if_directories_exist_and_make_if_not(download_path, temp_path, data_path)
    create_config()

    args = get_cli_args()
    setup_logging(args.verbosity)

    handle_cli(args)
