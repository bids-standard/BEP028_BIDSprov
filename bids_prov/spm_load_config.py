import re
import yaml
import os

# contains the path from home to the directory where this script is located
this_path = os.path.dirname(os.path.abspath(__file__))

PATH_REGEX = r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
PARAM_REGEX = r"[^\.]+\(\d+\)"  # balbla.fonc(53)
FILE_REGEX = r"(\.[a-z]{1,3}){1,2}"  #the string does not contain a filename so this is not an input_entity
DEPENDENCY_REGEX = r"""cfg_dep\(['"]([^'"]*)['"]\,.*"""  # TODO : add ": " in match

has_parameter = lambda line: re.search(PARAM_REGEX, line) is not None
# has_entity = lambda line: not has_parameter(line) and next(re.finditer(PATH_REGEX, line), None) is not None
# a string contains at least one parameter if  it does not start with a dot and contains at least one digit between
# brackets. if there are parameters, they are necessarily in the left part (function call) and this is not an entity
CONTEXT_URL = "https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json"

with open(this_path + "/spm_config.yml", "r") as fd:
    static = yaml.load(fd, Loader=yaml.CLoader)


def get_empty_graph(context_url=CONTEXT_URL):
    return {
        "@context": context_url,
        "BIDSProvVersion": "1.0.0",  # TODO ?
        "@id": "http://example.org/ds00000X",  # TODO ?
        "wasGeneratedBy": {
            "@id": "INRIA",
            "@type": "Project",
            "startedAt": "2016-09-01T10:00:00",  # TODO ?
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
                    "version": "dev"
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }


if __name__ == '__main__':
    # left_egal, right_egal = "channels.vols(1)", "cfg_dep('GunZip Files: GunZipped Files', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{':'}));"
    # print(has_parameter(left_egal))
    # print(has_parameter(right_egal))
    right = '0.9;'
    if not re.search(PATH_REGEX, right):
        print("if")
    else:
        print("pas if")