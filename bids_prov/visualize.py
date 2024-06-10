"""
A Command Line Interface to generate `graphviz` graphs from bids-prov JSON-ld files

This facilitates debugging and design of the specifications
"""

# import click
import argparse
import json
import os
import warnings
from collections import defaultdict

import pyld as ld
import rdflib as rl
import requests
from prov.dot import prov_to_dot
from prov.model import ProvDocument

OPTIONAL_FIELDS = {'Activity': ("startedAtTime", "endedAtTime"),
                   'Entity': ("atLocation", "generatedAt")}  # fields to omit if `--high-level` flag activated


def viz_turtle(content=None, img_file=None, source=None, **kwargs) -> None:

    prov_doc = ProvDocument.deserialize(
        content=content, format="rdf", rdf_format="turtle", source=source)
    # TODO : show attributes has optional arg
    dot = prov_to_dot(prov_doc, use_labels=True,
                      show_element_attributes=False, show_relation_attributes=False)
    dot.write_png(img_file)


def viz_jsonld11(jsonld11: dict, img_file: str) -> None:
    """
    jsonld11: dict
        a dictionary containing jsonld data,  usually obtained by calling `json.load`
    img_file: str
        output path
    """
    req_context_11 = requests.get(url=jsonld11["@context"])
    context_11 = req_context_11.json()
    context_10 = {
        k: v
        for k, v in context_11["@context"].items()
        if k not in {"@version", "Records"}
    }

    # Load graph from json-ld file as non 1.1 JSON-LD
    aa = ld.jsonld.compact(jsonld11, context_10)
    dataaa = json.dumps(aa, indent=2)  # , sort_keys=True)

    # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
    g = (rl.ConjunctiveGraph())
    g.parse(data=dataaa, format="json-ld")
    viz_turtle(content=g.serialize(format="turtle"), img_file=img_file)


def join_jsonld(lds: list, graph_key="Records", omit_details=True) -> dict:
    """
    lds: list of dict
        jsonld graphs to be joined

    omit_details: bool, default: True
        omit low level details like datetimes and paths
    Notes: assumes graph is typed indexed
    """
    ctx = set((_["@context"] for _ in lds))
    if not len(ctx) == 1:
        raise ValueError(f"jsonlds should have a common context, found {ctx}")
    payload = {"@context": next(iter(ctx)), graph_key: defaultdict(list)}
    for idx, ld in enumerate(lds, start=1):
        graph = ld.get(graph_key, dict())
        if not graph:
            warnings.warn(f"no graph found in jsonld file number {idx}")
        for _type, values in graph.items():
            if omit_details and _type[5:] in OPTIONAL_FIELDS.keys():
                values = [
                    {
                        k: d[k]
                        for k in d
                        if k not in OPTIONAL_FIELDS.get(_type[5:], tuple())
                    }
                    for d in values
                ]

            # FIXME check for duplicated defs
            payload[graph_key][_type].extend(values)

    if not payload[graph_key]:
        warnings.warn(
            f"could not found any {graph_key} section in the jsonlds")
    # payload[graph_key]] = dict(payload[graph_key]])
    return payload


def main(filename: str, output_file=None, omit_details=True) -> None:
    jsonld11s = list()
    with open(filename) as fd:
        ld = json.load(fd)
        jsonld11s.append(ld)

    # join multiple definitions
    jsonld11 = join_jsonld(jsonld11s, graph_key="Records",
                           omit_details=omit_details)

    if output_file is None:
        # replace extension .jsonld by .png
        output_file = (os.path.splitext(filename)[0] + ".png")

    viz_jsonld11(jsonld11, output_file)


def entry_point():
    """ A command line tool for the visualize module """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="res.jsonld", help="data jsonld file ")
    parser.add_argument("--output_file", type=str, default="res.png", help="output dir where results are written")
    opt = parser.parse_args()

    main(opt.input_file, output_file=opt.output_file, omit_details=True)
    # >> python -m   bids_prov.visualize --input_file ./res_temp.jsonld  --output_file res.png

if __name__ == "__main__":
    entry_point()
