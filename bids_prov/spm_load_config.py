import re
import yaml
import os

# contains the path from home to the directory where this script is located
this_path = os.path.dirname(os.path.abspath(__file__))

PARAM_REGEX = r"[^\.]+\(\d+\)"  # example: some_activity.function(53)
PATH_REGEX = r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
FILE_REGEX = r"(\.[a-z]{1,3}){1,2}"
DEPENDENCY_REGEX = r"""cfg_dep\(['"]([^'"]*)['"]\,.*"""  # TODO : add ": " in match
CONTEXT_URL = "https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json"


has_parameter = lambda line: re.search(PARAM_REGEX, line) is not None
# has_entity = lambda line: not has_parameter(line) and next(re.finditer(PATH_REGEX, line), None) is not None

with open(this_path + "/spm_config.yml", "r") as fd:
    static = yaml.load(fd, Loader=yaml.CLoader)


def get_empty_graph(context_url=CONTEXT_URL, spm_ver="dev"):
    return {
        "@context": context_url,
        "BIDSProvVersion": "dev",  # TODO ?
        "@id": "http://example.org/ds00000X",  # TODO ?
        "wasGeneratedBy": {
            "@id": "INRIA",
            "@type": "Project",
            "wasAssociatedWith": {
                "@id": "NIH",
                "@type": "Organization",
                "hadRole": "Funding",
            },
        },
        "records": {
            "prov:Agent": [
                {
                    "@id": "exampleAgentID",
                    "RRID": "RRID:SCR_007037",
                    "@type": "prov:SoftwareAgent",
                    "label": "SPM",
                    "version": spm_ver
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }

