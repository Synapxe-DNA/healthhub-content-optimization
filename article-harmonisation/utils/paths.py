import pathlib


def get_root_dir() -> str:
    """
    Retrieves the root directory of the project.

    This function calculates the absolute path to the root directory (healthhub-content-optimization)

    Returns:
        str: The absolute path to the root directory as a string.

    Example:
        root_dir = get_root_dir()
    """

    root_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    return root_dir


if __name__ == "__main__":
    ROOT_DIR = get_root_dir()
    print(ROOT_DIR)
