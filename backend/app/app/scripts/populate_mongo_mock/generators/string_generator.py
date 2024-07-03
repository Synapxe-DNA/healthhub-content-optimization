import random
import string


def random_str(length: int = 32) -> str:
    assert length > 0, "String length must be greater than zero!"

    letters = string.ascii_letters + " "
    return "".join(random.choice(letters) for i in range(length))


def random_id(length: int = 32) -> str:
    assert length > 0, "String length must be greater than zero!"

    letters = "ABCDEF" + string.hexdigits
    return "".join(random.choice(letters) for i in range(length))
