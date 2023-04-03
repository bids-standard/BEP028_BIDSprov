import uuid
import random
import hashlib
import os
import json

from typing import Mapping, Union, Tuple, Dict

CONTEXT_URL = "https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json"


def get_id():
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


def get_default_graph(label: str, context_url: str = CONTEXT_URL, soft_ver: str = "dev", ) \
        -> Tuple[Mapping[str, Union[str, Mapping]], str]:  # TODO Dict instead of Mapping , see parser graph["records"].update
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
                           "version": soft_ver
                       }
                   ],
                   "prov:Activity": [],
                   "prov:Entity": [],
               },
           }, agent_id


def label_mapping(label: str, mapping_filename: str) -> str:
    """
    A function that takes a label from matlab as a parameter and maps it if it is present in the json mapping file.

    Parameters
    ----------
    label : the label to be mapped

    mapping_filename : the name of the mapping file with its extension

    Returns
    -------
    str
        Returns either the mapped label or the label if not present in the mapping file

    """
    filedir = os.path.dirname(__file__)
    filepath = os.path.join(filedir, mapping_filename)
    with open(filepath) as f:
        mappings = json.load(f)

    for k_matlab, v_bids_prov in mappings.items():
        if k_matlab in label:
            return v_bids_prov
    else:
        return label


def get_sha256(file_path: str):
    m = hashlib.sha256()
    with open(file_path, 'rb') as f:
        lines = f.read()
        m.update(lines)
    md5code = m.hexdigest()
    return md5code


def writing_jsonld(graph, indent, output_file):
    """
    Write a json-ld in memory unless it already exists and contains the same content

    Parameters
    ----------
    graph : dict
        The content of the calculated json-ld graph
    indent : int
        The desired indentation of the json file
    output_file : str
        The desired file path

    Returns
    -------
    bool
        If the file already exists and contains the same content as `graph` then return True otherwise False.
    """
    if os.path.isfile(output_file):
        with open(output_file, "r") as f:
            existing_content = f.read()

            if existing_content == json.dumps(graph, indent=indent):
                return True
    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)
    return False