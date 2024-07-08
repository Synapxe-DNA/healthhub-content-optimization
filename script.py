import argparse
import shutil
from pathlib import Path

choices = {
    "data/01_raw",
    "data/02_intermediate",
    "data/03_primary",
    "data/04_feature",
    "data/05_model_input",
    "data/06_models",
    "data/07_model_output",
    "data/08_reporting",
}


def clean(
    directories: list[str],
    dry_run: bool | None = None,
    root_dir: str = "content-optimization",
) -> None:
    """
    Cleans the specified directories.

    Args:
        directories (list[str]): A list of directories to clean.
        dry_run (bool | None, optional): If True, the function will only simulate the cleaning process.
            If False, the function will actually delete the directories. Defaults to None.
        root_dir (str, optional): The root directory. Defaults to "content-optimization".

    Returns:
        None: This function does not return anything.
    """

    ask_for_confirmation = True

    for directory in directories:
        dir_path = Path(root_dir) / directory
        print(f"Cleaning {directory}")

        if dry_run is None:
            while ask_for_confirmation:
                confirmation = (
                    input("Are you sure you want to proceed? (Y/N/Q/skip): ")
                    .strip()
                    .lower()
                )
                if confirmation not in [
                    "y",
                    "n",
                    "q",
                    "skip",
                    "yes",
                    "no",
                    "quit",
                    "clear",
                ]:
                    print("Invalid confirmation")
                    continue
                elif confirmation in ["q", "quit", "clear"]:
                    return
                elif confirmation == "skip":
                    ask_for_confirmation = False
                    break
                break

            if confirmation in ["n", "no"]:
                print(f"Skipping {directory}")
                continue

        for path in dir_path.iterdir():
            # If it's a directory
            if not path.is_file():
                # If dry run is True
                if dry_run:
                    print(f"Would have deleted {path.stem}")
                else:
                    print(f"Deleted {path.stem}")
                    shutil.rmtree(path)  # Remove the directory and its contents

    print("Done!")


def main():
    """
    Main function that serves as the entry point of the script.

    This function parses command line arguments using the argparse module. It expects the following arguments:
    - --dirs:
        A list of directories to clean. The choices are:
            * "data/02_intermediate"
            * "data/03_primary"
            * "data/04_feature"
            * "data/05_model_input"
            * "data/06_models"
            * "data/07_model_output"
        This argument is optional and defaults to an empty list.
    - --dry-run:
        A flag that indicates whether the function should only print
        the directories to delete or actually delete them. This argument
        is optional and defaults to None.

    The function calls the clean function with the specified directories and dry run flag.

    Example usage:
        python script.py --dirs data/02_intermediate data/03_primary --dry-run
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dirs",
        choices=choices,
        default=[
            "data/02_intermediate",
            "data/03_primary",
            "data/04_feature",
            "data/05_model_input",
            "data/06_models",
            "data/07_model_output",
        ],
        type=str,
        help="directories to clean",
        nargs="*",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        help="if true, will only print the directories to delete",
    )

    args = parser.parse_args()
    clean(directories=args.dirs, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
