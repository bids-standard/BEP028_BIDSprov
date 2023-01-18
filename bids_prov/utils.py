import uuid
import random
import hashlib

from typing import Mapping, Union, Tuple

CONTEXT_URL = "https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json"


def get_id():
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


def get_default_graph(label: str, context_url: str = CONTEXT_URL, spm_ver: str = "dev",) \
        -> Tuple[Mapping[str, Union[str, Mapping]], str]:
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
                           "label": label,
                           "version": spm_ver
                       }
                   ],
                   "prov:Activity": [],
                   "prov:Entity": [],
               },
           }, agent_id


def get_sha256(file_path: str):
    m = hashlib.sha256()
    with open(file_path, 'rb') as f:
        lines = f.read()
        m.update(lines)
    md5code = m.hexdigest()
    return md5code
