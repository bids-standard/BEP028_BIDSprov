#!/usr/bin/python
# coding: utf-8

""" Merge the available provenance records of a BIDS dataset
    from JSON files into one RDF graph.
"""

from pathlib import Path
import json
from argparse import ArgumentParser
from io import StringIO

from pyld import jsonld

from rdflib import Dataset
from rdflib.namespace import PROV
from rdflib.plugins.sparql import prepareQuery

from bids import BIDSLayout
from bids.layout.models import BIDSFile, BIDSJSONFile

def get_associated_sidecar(layout: BIDSLayout, data_file: BIDSFile) -> dict:
    """ This function is a workaround to BIDSFile.get_associations function not working with
        derivative datasets.

        Return the associated sidecar of a BIDSFile in a given BIDSLayout.
        This returns None if no such sidecar exists.
    """
    filename = Path(data_file.path)
    extensions = ''.join(filename.suffixes)
    sidecar_filename = str(filename).replace(extensions, '.json')
    
    return layout.get_file(sidecar_filename)

def filter_provenance_group(files: list, group: str) -> list:
    """ Filter a given BIDSFile list, returning the sub-list containig the BIDS
    `prov` entity equal to group
    """
    return [f for f in files if f'prov-{group}' in f.filename]

def get_provenance_files(layout: BIDSLayout, suffix: str, group: str = None) -> list:
    """ Return a list of provenance files for the dataset. The list is filtered based on
        a given suffix and a given provenance group.
    """
    files = layout.get(suffix=suffix, invalid_filters='allow')

    if group is not None:
        return filter_provenance_group(files, group)
    return files

def get_described_datasets(layout: BIDSLayout) -> list:
    """ Return a list of dataset_description.json files that contain provenance description.
        Output files are returned as BIDSJSONFile.
        dataset_description.json contains provenance description if:
        - it contains a GeneratedBy field ;
        AND
        - at least one of the objects of the GeneratedBy has a Id field.
    """
    files = [f for f in layout.get() if f.filename == 'dataset_description.json']
    out_files = []

    for file in files:
        metadata = file.get_dict()
        if 'GeneratedBy' in metadata:
            for generated_by_obj in metadata['GeneratedBy']:
                if 'Id' in generated_by_obj:
                    out_files.append(file)
                    break

    return out_files

def get_described_files(layout: BIDSLayout) -> list:
    """ Return a list of files of the dataset for which provenance
        is described inside a sidecar JSON file.
    """
    return layout.get(GeneratedBy='', invalid_filters='allow', regex_search=True)

def get_described_sidecars(layout: BIDSLayout) -> list:
    """ Return a list of files of the dataset for which provenance
        of sidecar is described inside a sidecar JSON file.
    """
    return layout.get(SidecarGeneratedBy='', invalid_filters='allow', regex_search=True)

def get_dataset_entity_record(description_file: BIDSJSONFile) -> dict:
    """ Return an Entity provenance record from metadata of a BIDS dataset.
        We assume that provenance is described in the description_file, i.e.:
        - it contains a GeneratedBy field ;
        AND
        - at least one of the objects of the GeneratedBy has a Id field.
    """
    metadata = description_file.get_dict()

    # Provenance Entity record for the dataset
    entity = {
        "Id": "bids:current_dataset",
        "Label": metadata['Name'],
        "AtLocation": description_file.dirname,
        "GeneratedBy": []
    }

    # Get provenance-related metadata
    for generated_by_obj in metadata['GeneratedBy']:
        if 'Id' in generated_by_obj:
            entity['GeneratedBy'].append(generated_by_obj['Id'])

    return entity

def get_entity_record(layout: BIDSLayout, data_file: BIDSFile) -> dict:
    """ Return an Entity provenance record from metadata of a BIDS file
        in a given BIDSLayout.
    """

    # Provenance Entity record for the data file
    entity = {
        "Id": f"bids::{data_file.relpath}",
        "Label": data_file.filename,
        "AtLocation": data_file.path
    }

    # Get provenance-related metadata
    ## metadata = data_file.get_metadata()
    sidecar = get_associated_sidecar(layout, data_file)
    if sidecar is None:
        return None

    metadata = sidecar.get_dict()
    if 'GeneratedBy' in metadata:
        entity['GeneratedBy'] = metadata['GeneratedBy']
    if 'Digest' in metadata:
        entity['Digest'] = metadata['Digest']
    if 'Type' in metadata:
        entity['Type'] = metadata['Type']

    return entity

def get_sidecar_entity_record(layout: BIDSLayout, data_file: BIDSFile) -> dict:
    """ Return an Entity provenance record for the sidecar of a BIDS file, in a given BIDSLayout.
    """

    # Get sidecar associated with the data_file
    sidecar = get_associated_sidecar(layout, data_file)
    if sidecar is None:
        return None

    # Provenance Entity record for the sidecar JSON file
    entity = {
        "Id": f"bids::{sidecar.relpath}",
        "Label": sidecar.filename,
        "AtLocation": sidecar.path
    }

    # Get provenance-related metadata
    metadata = sidecar.get_dict()
    if 'SidecarGeneratedBy' in metadata:
        entity['GeneratedBy'] = metadata['SidecarGeneratedBy']
        return entity

    return None

def get_linked_entities(input_graph: dict) -> list:
    """ Return the Ids of Entity provenance records from the provenance graph
        that were either used or generated by an Activity.

        Arguments:
            - input_graph, dict: JSON-LD graph containing provenance records
        Return:
            - list: list of Entity provenance records from the graph that
            were either used or generated by an Activity
    """

    # Create RDF graph from input JSON-LD
    graph = Dataset()
    graph.parse(StringIO(json.dumps(jsonld.expand(input_graph))), format='json-ld')

    # Search for all prov:Entity GeneratedBy a prov:Activity in the graph
    query = prepareQuery("""
        SELECT ?s ?p ?o WHERE {
            ?s a prov:Entity .
            ?act a prov:Activity .
            ?s prov:wasGeneratedBy ?act .
            ?s ?p ?o .
        }
        GROUP BY ?s
        """,
        initNs = {'prov': PROV}
        )
    generated_entities = [s.n3(graph.namespace_manager).replace('<', '').replace('>', '')
        for s, _, _ in graph.query(query)]

    # Search for all prov:Entity used a prov:Activity in the graph
    query = prepareQuery("""
        SELECT ?s ?p ?o WHERE {
            ?s a prov:Entity .
            ?act a prov:Activity .
            ?act prov:used ?s .
            ?s ?p ?o .
        }
        GROUP BY ?s
        """,
        initNs = {'prov': PROV}
        )
    used_entities = [s.n3(graph.namespace_manager).replace('<', '').replace('>', '')
        for s, _, _ in graph.query(query)]

    # Return all linked prov:Entity
    return list(set(used_entities + generated_entities))

def merge_records(layout: BIDSLayout, group: str = None) -> dict:
    """ Merge provenace records of a dataset (`layout`) from the provenance group `group`.
        Return the JSON-LD version of the provenance description.
    """

    # Base for the output JSON-LD
    base_provenance = {
      "BIDSProvVersion": "0.0.1",
      "@context": "https://purl.org/nidash/bidsprov/context.json",
      "Records": {
        "Software": [],
        "Activities": [],
        "Entities": []
      }
    }

    # Get provenance metadata form provenance files
    for file in get_provenance_files(layout, suffix='ent', group=group):
        base_provenance['Records']['Entities'] += file.get_dict()['Entities']
    # TODO : add environment feature
    #for file in get_provenance_files(layout, suffix='env', group=group):
    #    base_provenance['Records']['Environments'] += file.get_dict()['Environments']
    for file in get_provenance_files(layout, suffix='act', group=group):
        base_provenance['Records']['Activities'] += file.get_dict()['Activities']
    for file in get_provenance_files(layout, suffix='soft', group=group):
        base_provenance['Records']['Software'] += file.get_dict()['Software']

    # Get provenance metadata from other JSON files in the dataset
    for data_file in get_described_files(layout):
        entity = get_entity_record(layout, data_file)
        if entity is not None:
            base_provenance['Records']['Entities'].append(entity)
    for data_file in get_described_sidecars(layout):
        entity = get_sidecar_entity_record(layout, data_file)
        if entity is not None:
            base_provenance['Records']['Entities'].append(entity)
    for dataset in get_described_datasets(layout):
        entity = get_dataset_entity_record(dataset)
        if entity is not None:
            base_provenance['Records']['Entities'].append(entity)

    # Filter on provenance group
    entities_in_group = get_linked_entities(base_provenance)
    entities = []
    for entity in base_provenance['Records']['Entities']:
        if entity['Id'] in entities_in_group:
            entities.append(entity)
    base_provenance['Records']['Entities'] = entities

    return base_provenance

def entry_point():
    """ A command line tool for the merge module """

    parser = ArgumentParser()
    parser.add_argument('--dataset', '-d', type=str, default='.',
        help='The path to the input BIDS dataset.')
    parser.add_argument('--derivative', action='store_true',
        help='Set this option to specify the dataset is a BIDS derivative dataset.')
    parser.add_argument('--output_file', '-o', type=str, required=True,
        help='Output JSON-LD file containing the provenance graph for the input dataset.')
    parser.add_argument('--group', '-g', type=str,
        help='Provenance group for which to extract the metadata.')
    arguments = parser.parse_args()

    # Write output JSON-LD file
    with open(arguments.output_file, 'w', encoding = 'utf-8') as file:
        file.write(
            json.dumps(merge_records(
                BIDSLayout(arguments.dataset, is_derivative=arguments.derivative),
                arguments.group
                ), indent = 2)
        )

if __name__ == '__main__':
    entry_point()
