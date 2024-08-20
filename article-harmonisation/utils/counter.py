import os

ROOT = os.getcwd()
print(ROOT)

# TODO: Check if counter.py is a relevant file. Remove if unneeded.


def add_count():
    file = open(
        f"{ROOT}/article-harmonisation/docs/txt_outputs/counter.txt",
        "r",
    )

    num = int(file.read())
    file.close()

    f = open(
        f"{ROOT}/article-harmonisation/docs/txt_outputs/counter.txt",
        "w",
    )
    print(num + 1, file=f)
