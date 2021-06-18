from typing import Mapping, Union

from boutiques.searcher import Searcher
from boutiques.puller import Puller

import json
from bids_prov import get_or_load

DEFAULT_CONTEXT_URL = "https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json"

TYPES = (
    "File",
    # "String",
    "Number",
    "Flag",
)


@get_or_load
def get_config(agent: str) -> Mapping[str, Mapping[str, object]]:
    """get a config by querying bosh with `agent`

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


def get_default_graph(context_url: str) -> Mapping[str, Union[str, Mapping]]:
    return {
        "@context": context_url,
        "@id": "http://example.org/ds00000X",
        "generatedAt": "2020-03-10T10:00:00",
        "wasGeneratedBy": {
            "@id": "INRIA",
            "@type": "Project",
            "startedAt": "2016-09-01T10:00:00",
            "wasAssociatedWith": {
                "@id": "NIH",
                "@type": "Organization",
                "hadRole": "Funding",
            },
        },
        "records": {
            "prov:Agent": [
                {
                    "@id": "RRID:SCR_002823",  # TODO query for version
                    "@type": "prov:SoftwareAgent",
                    "label": "FSL",
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }
