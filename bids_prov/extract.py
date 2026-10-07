#!/usr/bin/python
# coding: utf-8

""" Generate a subgraph with elements connected to a given node. """

import json
from io import StringIO

from pyld import jsonld

from rdflib import Dataset
from rdflib.plugins.sparql import prepareQuery

""" Extract the subgraph corresponding to all nodes connected to a given node.
    This was design for prov:Entity as starting node, to show the whole process
    that was needed to generate this prov:Entity.
 """

def entry_point(input_file: str, node_id: str, output_file: str) -> None:
    """ Search for all nodes linked to a prov:Entity """

    # Open and read input file
    with open(input_file, 'r', encoding='utf-8') as file:
        base_provenance = json.load(file)

    # Input data as a RDF graph
    graph = Dataset()
    graph.parse(StringIO(json.dumps(jsonld.expand(base_provenance))), format='json-ld')

    # Query to construct the sub graph
    """
    Source: https://stackoverflow.com/questions/37186530/how-do-i-construct-get-the-whole-sub-graph-from-a-given-resource-in-rdf-graph

    This works because every property is either <> or not, so <>|!<> matches every property,
    and then (<>|!<>)* is an arbitrary length path, including paths of length zero,
    which means that ?s will be bound to everything reachable from :a, including :a itself.
    Then you're grabbing the triples where ?s is the subject.
    When you construct the graph of all those triples, you get the subgraph connected to :a.
    """
    query = prepareQuery(f"""
        CONSTRUCT {{ ?s ?p ?o }} WHERE {{
            <{node_id}> (<>|!<>)* ?s .
            ?s ?p ?o .
            }}
        """
        )

    # List of Ids to keep as they are connected to the starting node
    connected_nodes = [s.n3(graph.namespace_manager).replace('<', '').replace('>', '')
        for s, _, _ in graph.query(query)]

    # Exclude objects that are not connected nodes
    for key in base_provenance['Records'].keys():
        objects = []
        for node in base_provenance['Records'][key]:
            if node['Id'] in connected_nodes:
                objects.append(node)
        base_provenance['Records'][key] = objects

    # Write output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(json.dumps(base_provenance, indent=4))
