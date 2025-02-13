# BIDS-Prov example for nipype

This example aims at showing provenance traces from a simple [nipype](https://nipype.readthedocs.io/en/latest/) workflow, performed on a container-based software environment.

## Workflow

The workflow code is inside `code/normalize.py` and performs:
1. a brain extraction of a T1w anatomical file `sub-001/anat/sub-001_Tw.nii.gz`, using BET;
2. a normalisation to MNI152 of the resulting file, using FLIRT;
3. exporting relevant output files to a BIDS compliant name space.

See [hereafter](#running-the-workflow) for more details on how to run the workflow.

## Overview

In order to describe provenance records using BIDS Prov, we use:

* the `GeneratedBy` field of JSON sidecar files, already existing in the BIDS specification;
* modality agnostic files inside the `prov/` directory
* a modality agnostic file inside the `derivatives/normalize/sub-001/anat/` directory

After running the workflow and adding provenance traces, the resulting directory tree looks like this:

```
.
├── code
│   └── normalize.py
├── derivatives
│   ├── bids_prov_workflow
│   └── normalize
│       └── sub-001
│           └── anat
│               ├── sub-001_prov-normalize_act.prov.json
│               ├── sub-001_space-mni152nlin2009casym_T1w_brain.json
│               ├── sub-001_space-mni152nlin2009casym_T1w_brain.nii.gz
│               ├── sub-001_T1w_brain.json
│               └── sub-001_T1w_brain.nii.gz
├── prov
│   ├── prov-normalize_base.prov.json
│   ├── prov-normalize_ent.prov.json
│   ├── prov-normalize_env.prov.json
│   └── prov-normalize_soft.prov.json
├── README.md
└── sub-001
    └── anat
        └── sub-001_T1w.nii.gz

```

Note that the `derivatives/bids_prov_workflow/` directory is nipype's working directory for the workflow. Its contents are not exhaustively described by the provenance traces.

## Provenance merge

The python script `code/merge_prov.py` aims at merging all provenance records into one JSON-LD graph.

```shell
pip install bids-prov==0.1.0
mkdir prov/merged/
python code/merge_prov.py
```

The `code/merge_prov.py` code is responsible for:
* merging the JSON provenance traces into the base JSON-LD graph;
* create an `Entity` and linking it to the `Activity` described by the `GeneratedBy` field in the case of JSON sidecars.

## Provenance visualization

We are then able to visualize these provenance files using the following commands (current directory is `examples/nipype/`):

```shell
pip install bids-prov==0.1.0
bids_prov_visualizer --input_file prov/merged/prov-normalize.prov.jsonld --output_file prov/merged/prov-normalize.prov.png
```

![](/examples/nipype/prov/merged/prov-normalize.prov.png)

## Running the workflow

We use of the `nipype/nipype:py38` docker image that contains both nipype and FSL.

Assuming we are inside the nipype example directory (`examples/nipype`)

```bash
# Get the container and run the workflow
docker pull nipype/nipype:py38
docker run -u root -it --rm -v .:/work nipype/nipype:py38 python code/normalize.py
```

## Limitations
