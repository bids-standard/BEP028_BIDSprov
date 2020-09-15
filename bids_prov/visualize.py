"""
A Command Line Interface to generate `graphviz` graphs from bids-prov JSON-ld files

This facilitates debugging and design of the specifications
"""

import click
from graphviz import Digraph
import json

from prov.model import ProvDocument
from prov.dot import prov_to_dot
import requests
import os

import rdflib as rl
import pyld as ld
import json

def viz_turtle(source=None, content=None, img_file=None, disp=True):
    prov_doc = ProvDocument.deserialize(source=source, content=content, format='rdf', rdf_format='turtle')

    dot = prov_to_dot(prov_doc, use_labels=True)
    dot.write_png(img_file)


def viz_jsonld11(jsonld11_file, img_file, disp=True):
    url_context11 = json.load(open(jsonld11_file))

    req_context_11 = requests.get(url=url_context11['@context'])
    context_11 = req_context_11.json()

    context_10 = {k: v for k,v in context_11['@context'].items() if k not in {'@version', 'records'}}

    # Load graph from json-ld file as non 1.1 JSON-LD
    aa=ld.jsonld.compact(
        json.load(open(jsonld11_file, 'r')),
        context_10)

    g = rl.ConjunctiveGraph()
    g.parse(data=json.dumps(aa, indent=2), format='json-ld')

    viz_turtle(content=g.serialize(format='turtle').decode(), img_file=img_file, disp=disp)



@click.command()
@click.argument('filenames', nargs=-1)
@click.option('--output_file', '-o', default='')
def main(filenames, output_file):
    filename = filenames[0]  # FIXME handle graph across multiple files

    if not output_file:
        output_file = os.path.splitext(filename)[0] + '.png'

    viz_jsonld11(filename, output_file)


if __name__ == '__main__':
    main()