import re
import yaml
import os

from . import get_id

this_path = os.path.dirname(os.path.abspath(__file__))

PATH_REGEX = r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
PARAM_REGEX = r"[^\.]+\(\d+\)"
FILE_REGEX = r"(\.[a-z]{1,3}){1,2}"
DEPENDENCY_REGEX = r"""cfg_dep\(['"]([^'"]*)['"]\,.*"""  # TODO : add ": " in match

has_parameter = lambda line: next(re.finditer(PARAM_REGEX, line), None) is not None
# has_entity = lambda line: not has_parameter(line) and next(re.finditer(PATH_REGEX, line), None) is not None

CONTEXT_URL = "https://purl.org/nidash/bidsprov/context.json"

with open(this_path + "/spm_config.yml", "r") as fd:
    static = yaml.load(fd)


def get_empty_graph(context_url=CONTEXT_URL):
    return {
        "@context": context_url,
        "BIDSProvVersion": "1.0.0",
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
                    "@id": get_id(),
                    "rrid": "RRID:SCR_007037",  # TODO query for version
                    "@type": "prov:SoftwareAgent",
                    "label": "SPM",
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }
