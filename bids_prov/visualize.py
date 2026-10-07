#!/usr/bin/python
# coding: utf-8

""" A Command Line Interface to generate `graphviz` graphs from bids-prov JSON-LD files.
    This facilitates debugging and design of the specifications.
"""

import json
from os.path import splitext

import requests
from pyld.jsonld import compact
from rdflib import Dataset
from prov.dot import prov_to_dot
from prov.model import ProvDocument

def turtle_to_image(turtle: str, output_file: str, detailed: bool) -> None:
    """ Write PNG graph visualization from RDF turtle graph content.

        turtle: str,
            Graph as turtle content
        output_file: str,
            Name of the output PNG file
        detailed: bool,
            Provide graph with more information
    """
    # Open turtle content as a prov document
    prov_doc = ProvDocument.deserialize(content=turtle, format='rdf', rdf_format='turtle')

    # Convert prov document to dot format
    dot_data = prov_to_dot(
        prov_doc,
        use_labels=True,
        show_element_attributes=detailed,
        show_relation_attributes=detailed
        )

    # Write output file
    dot_data.write_png(output_file)

def jsonld11_to_jsonld10(jsonld_11: dict) -> dict:
    """ Convert JSON-LD 1.1 data into JSON-LD 1.0 data.
        TODO: how / what ? Without type indexing

        jsonld_11: dict
            JSON-LD data, usually obtained by calling `json.load`

        Return JSON-LD 1.1 data as a dict
    """
    # Get context data from the provided URL
    req_context_11 = requests.get(url=jsonld_11['@context'])

    # Convert JSON-LD 1.1 context data to JSON-LD 1.0
    context_11 = req_context_11.json()
    context_10 = {
        k: v
        for k, v in context_11['@context'].items()
        if k not in {'@version', 'Records'}
    }

    # Return JSON-LD 1.0 data
    return compact(jsonld_11, context_10)

def jsonld10_to_turtle(jsonld_10: dict) -> str:
    """ Convert JSON-LD data to RDF turtle.

        jsonld_10: str,
            input JSON-LD data

        Return turtle data as a string
    """
    # Load JSON-LD data into a rdflib Dataset
    graph = Dataset()
    graph.parse(data=json.dumps(jsonld_10), format='json-ld')

    # Serialize to turtle
    return graph.serialize(format='turtle')

def entry_point(filename: str, output_file:str, detailed:bool) -> None:
    """ Entry point to convert JSON-LD data to a PNG RDF graph
        filename: str,
            name of the file containing JSON-LD data
        output_file: str,
            optional name for the output PNG file
        detailed: bool,
            If false: omit low level details like datetimes and paths
    """

    # Handle multiple files ?
    #join_jsonld(graph_data, omit_details=not detailed)

    # Read JSON-LD data from file
    with open(filename, 'r', encoding='utf-8') as file:
        graph_data = json.load(file)

    graph_data = jsonld11_to_jsonld10(graph_data)
    graph_data = jsonld10_to_turtle(graph_data)

    # Name for the output file
    if output_file is None:
        # Replace extension .jsonld by .png
        output_file = (splitext(filename)[0] + '.png')

    # Write PNG file
    turtle_to_image(graph_data, output_file, detailed)
