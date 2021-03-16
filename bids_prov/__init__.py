import os
import json
from os.path import expanduser

import string
import random
# TODO uuid from special library (20 alpha num)
# https://stackoverflow.com/questions/41186818/how-to-generate-a-random-uuid-which-is-reproducible-with-a-seed-in-python

# generates a string containing 20 letters (upper or lower case, 52 possible characters)


def get_id():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(20))


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
