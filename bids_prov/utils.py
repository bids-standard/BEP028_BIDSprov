import hashlib
import json
import os
import random
import shutil
import uuid
from typing import Mapping, Union, Tuple

CONTEXT_URL = "https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json"


def get_id():
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


def get_default_graph(label: str, context_url: str = CONTEXT_URL, soft_ver: str = "dev", ) \
        -> Tuple[Mapping[str, Union[str, Mapping]], str]:  # TODO Dict instead of Mapping , see parser graph["Records"].update
    agent_id = get_id()
    return {
               "@context": context_url,
               "BIDSProvVersion": "dev",  # TODO ?
               "Records": {
                   "prov:Agent": [
                       {
                           "@id": "urn:" + agent_id,
                           "RRID": "RRID:SCR_007037",
                           "@type": "prov:SoftwareAgent",
                           "Label": label,
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
    sha256code = m.hexdigest()
    return sha256code


def compute_sha_256_entity(entities: dict):
    """
    This method calculates the sha256 of all entities if they contain the key "AtLocation".
    If the file does not exist, then it is generated.

    Parameters
    ----------
    entities : dict
        The prov:Entity part of our dictionary generated in bids-prov format

    Returns
    -------
    None
    """
    directory = 'bids_prov/file_generation'
    for entity in entities:
        if "AtLocation" in entity:
            if len(entity["AtLocation"]) > 0:
                if entity["AtLocation"][0] == "/":
                    relative_path = os.path.abspath(directory + entity["AtLocation"])
                else:
                    relative_path = os.path.abspath(directory + "/" + entity["AtLocation"])

                # Temporary process. If the file does not exist then it is created to have a digest value
                file_directory = os.path.dirname(relative_path)
                if not os.path.exists(file_directory):
                    os.makedirs(file_directory)

                if not os.path.exists(relative_path):
                    try:
                        with open(relative_path, 'w') as f:
                            f.write(relative_path)
                    except NotADirectoryError as e:
                        print(f"The file {relative_path} is the child of a parent folder that was created as a file "
                              f"previously. To be fixed.")

                if os.path.exists(relative_path):
                    try:
                        sha256_value = get_sha256(relative_path)
                        checksum_name = "sha256"
                        entity['digest'] = {checksum_name: sha256_value}
                    except IsADirectoryError as e:
                        print(f"The file {relative_path} is a directory and also a file. To be fixed.")

    if os.path.exists(directory):
        shutil.rmtree(directory)


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
