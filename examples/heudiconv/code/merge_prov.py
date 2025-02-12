#!/usr/bin/python
# coding: utf-8

""" Merge available prov JSON files into one JSON-LD graph """

import json
from pathlib import Path

# List of available prov files
prov_soft_files = [
	'prov/prov-heudiconv_soft.prov.json'
]
prov_env_files = [
	'prov/prov-heudiconv_env.prov.json'
]
prov_act_files = [
	'prov/prov-heudiconv_act.prov.json'
]
prov_ent_files = [
	'prov/prov-heudiconv_ent.prov.json'
]
sidecar_files = [
	'sub-001/sub-001_scans.json',
	'sub-001/anat/sub-001_run-1_T1w.json'
]

# Base jsonld
base_provenance = {
  "Records": {
    "Software": [],
    "Activities": [],
    "Entities": []
  }
}

# Add context and version
with open('prov/prov-heudiconv_base.prov.json', encoding = 'utf-8') as file:
	base_provenance.update(json.load(file))

# Parse Software
for prov_file in prov_soft_files:
	with open(prov_file, encoding = 'utf-8') as file:
		data = json.load(file)
		for key, value in data.items():
			value['Id'] = key
			base_provenance['Records']['Software'].append(value)

# Parse Environments
for prov_file in prov_env_files:
	with open(prov_file, encoding = 'utf-8') as file:
		data = json.load(file)
		for key, value in data.items():
			value['Id'] = key
		 	# /!\ Workaround: environments are added in the Entities list because
		 	# the Environments term is not defined in the BIDS Prov context yet
			base_provenance['Records']['Entities'].append(value)

# Parse Activities
for prov_file in prov_act_files:
	with open(prov_file, encoding = 'utf-8') as file:
		data = json.load(file)
		for key, value in data.items():
			value['Id'] = key
			base_provenance['Records']['Activities'].append(value)

# Parse Entities
for prov_file in prov_ent_files:
	with open(prov_file, encoding = 'utf-8') as file:
		data = json.load(file)
		for key, value in data.items():
			value['Id'] = key
			base_provenance['Records']['Entities'].append(value)

# Parse Sidecar files
for sidecar_file in sidecar_files:
	# Identify data file(s) associated with the sidecar
	sidecar_filename = Path(sidecar_file)
	data_files = Path('').glob(f'{sidecar_filename.with_suffix("")}.*')
	data_files = [str(f) for f in list(data_files) if str(sidecar_filename) not in str(f)]

	# Write provenance
	with open(sidecar_file, encoding = 'utf-8') as file:
		data = json.load(file)
		if 'GeneratedBy' in data:
			activity_id = data['GeneratedBy']
			for data_file in data_files:
				base_provenance['Records']['Entities'].append({
					"Id": f"bids::{data_file}",
					"GeneratedBy": activity_id
					})

# Write jsonld
with open('prov/merged/prov-heudiconv.prov.jsonld', 'w', encoding = 'utf-8') as file:
	file.write(json.dumps(base_provenance, indent = 2))
