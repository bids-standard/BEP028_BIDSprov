import os
import json
from os.path import expanduser

import string
import random


def get_id(size=10):
    return "".join(random.choice(string.ascii_letters) for _ in range(size))


def get_or_load(fn):
    """
    fn should return a json serializable object

    results will be stored in the home directory ('~')
    """

    def wrapper(*args, **kwargs):
        filename = os.path.join(expanduser("~"), fn.__name__)
        filename += "_".join(args)
        filename += ".json"
        if os.path.exists(filename):
            print(f"loading dumped results from {filename}")
            with open(filename, "r") as fd:
                d = json.load(fd)
                return d
        else:
            d = fn(*args, **kwargs)
            with open(filename, "w") as fd:
                json.dump(d, fd)
            return d

    return wrapper
