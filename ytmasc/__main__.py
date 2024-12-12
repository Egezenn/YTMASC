"Handles all things regarding CLI arguments, launches UI"
from .intermediates_cli import get_cli_args, handle_cli
from .utility import (
    check_if_directories_exist_and_make_if_not,
    data_path,
    download_path,
    temp_path,
)

if __name__ == "__main__":
    check_if_directories_exist_and_make_if_not(download_path, temp_path, data_path)

    args = get_cli_args()

    handle_cli(args)
