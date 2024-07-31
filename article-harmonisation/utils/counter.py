import os

ROOT = os.getcwd()
print(ROOT)


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
