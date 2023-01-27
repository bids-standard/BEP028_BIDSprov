import json
import os

from typing import Mapping, Union
from os.path import expanduser
from boutiques.searcher import Searcher
from boutiques.puller import Puller


TYPES = (
    "File",
    # "String",
    "Number",
    "Flag",
)


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


@get_or_load
def get_config(agent: str) -> Mapping[str, Mapping[str, object]]:
    """get a config by querying bosh (tool to access Boutiques documents, see https://boutiques.github.io/) with `agent`
    eq to running ```bosh search``` from the command-line
    """
    searcher = Searcher(agent)
    results = searcher.search()
    ids = [_["ID"] for _ in results]
    paths = Puller(ids).pull()
    res = dict()
    for path, result in zip(paths, results):
        try:
            with open(path, "r") as fd:
                d = json.load(fd)
        except Exception:
            print(f"could not load config from {result['TITLE']}")
            continue
        res[result["TITLE"]] = d

    return res


bosh_config = get_config("fsl")
