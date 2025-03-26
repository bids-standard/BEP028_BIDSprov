#!/usr/bin/python
# coding: utf-8

""" Convert nipype provenance traces into one BIDS-Prov compliant JSON-LD graph """

import json
from pyld import jsonld
from rdflib import Dataset, Graph, Namespace
from rdflib.namespace import RDF, RDFS, PROV
from rdflib.plugins.sparql import prepareQuery

from queries import queries, simple_queries

# Dict of namespaces to be used in queries
NAMESPACES = {
    'rdfs': RDFS,
    'rdf': RDF,
    'prov': PROV,
    'nipype': Namespace("http://nipy.org/nipype/terms/"),
    'niiri': Namespace("http://iri.nidash.org/"),
    'crypto': Namespace("http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/"),
    'bidsprov': Namespace("https://github.com/bids-standard/BEP028_BIDSprov/terms/")
}

# Parse the nipype RDF provenance file
# We use Dataset as there might be several graphs in the file
nipype_prov = Dataset()
nipype_prov.parse('prov/workflow_provenance_20250314T155959.trig', format='trig')

# Create an empty graph for output provenance
bids_prov = Graph()

# Query input graph
for label, query in simple_queries.items():
    print(label)
    q = prepareQuery(query, initNs = NAMESPACES)
    for graph in nipype_prov.graphs():
        queried_graph = graph.query(q)
        if len(queried_graph) > 0:
            bids_prov += queried_graph

# Serialize output graph to JSON-LD and compact
compacted = jsonld.compact(
    json.loads(bids_prov.serialize(format='json-ld')),
    'https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json'
    )

# Write compacted JSON-LD
with open('prov/workflow_provenance_20250314T155959_compacted.jsonld', 'w', encoding='utf-8') as file:
    file.write(json.dumps(compacted, indent=2))

# Merge records into a BIDS-Prov skeleton
bids_prov_skeleton = {
  "@context": "https://raw.githubusercontent.com/bids-standard/BEP028_BIDSprov/master/context.json",
  "BIDSProvVersion": "0.0.1",
  "Records": {
    "Software": [],
    "Activities": [],
    "Entities": [],
    "Environments": []
  }
}
for record in compacted['@graph']:
    if 'Type' not in record:
        continue
    if record['Type'] == 'Software':
        bids_prov_skeleton['Records']['Software'].append(record)
    elif record['Type'] == 'Activities':
        bids_prov_skeleton['Records']['Activities'].append(record)
    elif 'Environment' in record['Type']:
        bids_prov_skeleton['Records']['Environments'].append(record)
    else:
        bids_prov_skeleton['Records']['Entities'].append(record)

# Write BIDS-Prov JSON-LD
with open('prov/workflow_provenance_20250314T155959_bidsprov.jsonld', 'w', encoding='utf-8') as file:
    file.write(json.dumps(bids_prov_skeleton, indent=2))
