import hashlib
import json
import os
import random
import string
import shutil
import uuid
from rfc3986 import normalize_uri
from typing import Mapping, Union, Tuple
import re

CONTEXT_URL = "https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json"
SOFTWARE_RRIDS = {
        'AFNI': 'RRID:SCR_005927',
        'FSL': 'RRID:SCR_002823',
        'SPM': 'RRID:SCR_007037'
    }

def get_uuid() -> str:
    return str(uuid.UUID(int=random.getrandbits(128), version=4))

def get_random_string(length: str = 8) -> str:
    """ Return a random string of a given length.
        The string may contain uppercase letters,
        lowercase letters, and digits.

    Parameters
    ----------
    length : length of the output string

    Returns
    -------
    str : a random string
    """
    return ''.join(random.choices(
        string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))

def get_rrid(soft_label: str):
    """ Return the RRID (see: https://rrid.site/about/Getting%20Started) for a software

    Parameters
    ----------
    soft_label : the label of the software (e.g.: FSL, SPM, etc.)

    Returns
    -------
    str : the RRID of the software
    or None if the software is not referenced in SOFTWARE_RRIDS
    """
    if soft_label in SOFTWARE_RRIDS:
        return SOFTWARE_RRIDS[soft_label]

    return None

def make_alnum(input_string: str) -> str:
    """ Remove all non alphanumeric form a string

    Parameters
    ----------
    input_string : string to make alphanumeric

    Returns
    -------
    str : input string with all non alphanumeric removed
    """
    return re.sub(re.compile(r'[^a-zA-Z0-9]'), '', input_string)

def get_activity_urn(label: str) -> str:
    """ Return a randomly generated yet human readable URN for a bids prov Activity

    Parameters
    ----------
    label : the label of the Activity

    Returns
    -------
    str : a new URN for the Activity
    """
    return f'urn:{make_alnum(label)[:8].lower()}-{get_random_string()}'

def get_agent_urn(label: str) -> str:
    """ Return a randomly generated yet human readable URN for a bids prov Agent

    Parameters
    ----------
    label : the label of the Agent

    Returns
    -------
    str : a new URN for the Agent
    """
    return f'urn:{make_alnum(label)[:8].lower()}-{get_random_string()}'

def get_entity_urn(label: str, dataset: str = '') -> str:
    """ Return a URN for a bids prov Entity, based on a given label and the
    id of the BIDS dataset.

    Parameters
    ----------
    label : the label of the entity
    dataset : id of the BIDS dataset

    Returns
    -------
    str : a new URN for the entity
    """
    return f'bids:{dataset}:{normalize_uri(label)}'

def get_default_graph(soft_label: str, soft_version: str = "dev", context_url: str = CONTEXT_URL) \
        -> Tuple[Mapping[str, Union[str, Mapping]], str]:  # TODO Dict instead of Mapping , see parser graph["Records"].update
    """ Return the base graph for a bids prov file

    Parameters
    ----------
    soft_label : the label of the software generating the provenance tracks (e.g.: FSL, SPM, etc.)
    soft_version : the version of the software generating the provenance tracks
    context_url : the url to the json context

    Returns
    -------
    tuple :
        mapping : the base graph
        str : the id generated for the software
    """
    agent_id = get_agent_urn(soft_label)
    software_record = {
        "@id": agent_id,
        "@type": "prov:SoftwareAgent",
        "Label": soft_label,
        "Version": soft_version
       }

    agent_rrid = get_rrid(soft_label)
    if agent_rrid is not None:
        software_record["AltIdentifier"] = get_rrid(soft_label)

    return {
        "@context": context_url,
        "BIDSProvVersion": "dev",
        "Records": {
            "Software": [
                software_record
            ],
            "Activities": [],
            "Entities": [],
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


def simplify_urns(graph: str) -> str:
    """
    Replace URNs of a json-ld graph with simpler (not random) values defined by their order of appearance in the graph.

    Parameters
    ----------
    graph : str
        The json-ld graph dumped as a string

    Returns
    -------
    str
        The input string with simplified urns.
    """

    # Get all occurrences of ("urn:" + 36 following chars)
    urn_occurrences = [i for i in re.finditer(r'urn:[a-zA-Z0-9\-]{36}', graph)]

    # Prepare a dict in which :
    #     - key is an urn as present in the original graph
    #     - value is an id corresponding to the order of appearance of the urn in the graph.
    known_urns = dict()
    counter = 0

    # Assign one simpler id to each urn
    for urn in urn_occurrences:
        if urn.group() not in known_urns:
            known_urns[urn.group()] = f"urn:{str(counter).zfill(36)}"
            counter += 1

    # Replace all urns in the input graph with their assigned id
    output_graph = graph
    for key, value in known_urns.items():
        output_graph = output_graph.replace(key, value)

    return output_graph


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
            existing_content = simplify_urns(f.read())

        new_content = simplify_urns(json.dumps(graph, indent=indent))

        if existing_content == new_content:
            return True

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)
    return False
