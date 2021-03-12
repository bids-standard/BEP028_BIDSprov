import re

PATH_REGEX = r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
PARAM_REGEX = r"[^\.]+\(\d+\)"
FILE_REGEX = r"(\.[a-z]{1,3}){1,2}"
DEPENDENCY_REGEX = r"""cfg_dep\(['"]([^'"]*)['"]\,.*"""  # TODO : add ": " in match

has_parameter = lambda line: next(re.finditer(PARAM_REGEX, line), None) is not None
# has_entity = lambda line: not has_parameter(line) and next(re.finditer(PATH_REGEX, line), None) is not None

DEPENDENCY_DICT = dict(Segment="spatial.preproc")

CONTEXT_URL = "https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json"


def get_empty_graph(context_url=CONTEXT_URL):
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
                    "@id": "RRID:SCR_007037",  # TODO query for version
                    "@type": "prov:SoftwareAgent",
                    "label": "SPM",
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }
