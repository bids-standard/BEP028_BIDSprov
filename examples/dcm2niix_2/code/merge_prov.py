#!/usr/bin/python
# coding: utf-8

""" Merge available prov JSON-LD files into one JSON-LD graph """

import json
from bids_prov.visualize import join_jsonld

# List of available prov files
prov_files = [
	'prov/software.prov.jsonld',
	'prov/environments.prov.jsonld',
	'sub-02/anat/sub-02_T1w.prov.jsonld'
]

# Generate JSON-LD graph of each file using pyld
graphs = list()
for prov_file in prov_files:
	with open(prov_file, encoding = 'utf-8') as file:
		graphs.append(json.load(file))

# Merge graphs & Write JSON-LD graph
with open('prov/merged/dcm2niix.prov.jsonld', 'w' , encoding = 'utf-8') as file:
	file.write(json.dumps(join_jsonld(graphs, omit_details = False), indent = 2))
