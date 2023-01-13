import re
import yaml
import os
import hashlib

from bids_prov.utils import get_id

# contains the path from home to the directory where this script is located
this_path = os.path.dirname(os.path.abspath(__file__))

PATH_REGEX = r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
PARAM_REGEX = r"[^\.]+\(\d+\)"  # example: some_activity.function(53)
FILE_REGEX = r"(\.[a-z]{1,3}){1,2}"  # the string does not contain a filename so this is not an input_entity
DEPENDENCY_REGEX = r"""cfg_dep\(['"]([^'"]*)['"]\,.*"""  # TODO : add ": " in match
CONTEXT_URL = "https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json"


has_parameter = lambda line: re.search(PARAM_REGEX, line) is not None
# has_entity = lambda line: not has_parameter(line) and next(re.finditer(PATH_REGEX, line), None) is not None

with open(this_path + "/spm_config.yml", "r") as fd:
    static = yaml.load(fd, Loader=yaml.CLoader)


def get_sha256(file_path):
    m = hashlib.sha256()
    with open(file_path,'rb') as f:
        lines = f.read()
        m.update(lines)
    md5code = m.hexdigest()
    return md5code


def get_empty_graph(context_url=CONTEXT_URL, spm_ver="dev"):
    agent_id = get_id()
    return {
        "@context": context_url,
        "BIDSProvVersion": "dev",  # TODO ?
        "@id": "http://example.org/ds00000X",  # TODO ?
        "records": {
            "prov:Agent": [
                {
                    "@id": "urn:" + agent_id,
                    "RRID": "RRID:SCR_007037",
                    "@type": "prov:SoftwareAgent",
                    "label": "SPM",
                    "version": spm_ver
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }, agent_id

