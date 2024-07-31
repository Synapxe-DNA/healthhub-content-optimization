import pathlib


def get_root_dir() -> str:
    root_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    return root_dir


if __name__ == '__main__':
    ROOT_DIR = get_root_dir()
    print(ROOT_DIR)