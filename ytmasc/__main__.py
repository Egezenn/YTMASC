"Handles all things regarding CLI arguments, launches UI"
from .intermediates_cli import get_cli_args, handle_cli
from .utility import (
    check_if_directories_exist_and_make_if_not,
    check_if_file_exists_copy_if_not,
    data_path,
    download_path,
    temp_path,
    yaml_config,
    yaml_default_config,
)

if __name__ == "__main__":
    check_if_directories_exist_and_make_if_not(download_path, temp_path, data_path)
    check_if_file_exists_copy_if_not(yaml_default_config, yaml_config)

    args = get_cli_args()

    handle_cli(args)
