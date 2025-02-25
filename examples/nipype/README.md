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
* a modality agnostic file inside the `derivatives/flirt/sub-001/anat/` directory

After running the workflow and adding provenance traces, the resulting directory tree looks like this:

```
.
├── code
│   └── normalize.py
├── derivatives
│   ├── bids_prov_workflow
│   └── flirt
│       ├── prov
│       │   ├── prov-flirt_base.prov.json
│       │   ├── prov-flirt_ent.prov.json
│       │   ├── prov-flirt_env.prov.json
│       │   └── prov-flirt_soft.prov.json
│       └── sub-001
│           └── anat
│               ├── sub-001_prov-flirt_act.prov.json
│               ├── sub-001_space-mni152nlin2009casym_T1w_brain.json
│               ├── sub-001_space-mni152nlin2009casym_T1w_brain.nii.gz
│               ├── sub-001_T1w_brain.json
│               └── sub-001_T1w_brain.nii.gz
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
bids_prov_visualizer --input_file prov/merged/prov-flirt.prov.jsonld --output_file prov/merged/prov-flirt.prov.png
```

![](/examples/nipype/prov/merged/prov-flirt.prov.png)

## Running the workflow

We use of the `nipype/nipype:py38` docker image that contains both nipype and FSL.

Assuming we are inside the nipype example directory (`examples/nipype`)

```bash
# Get the container and run the workflow
docker pull nipype/nipype:py38
docker run -u root -it --rm -v .:/work nipype/nipype:py38 python code/normalize.py
```

## Limitations / open questions

1. We are not able yet to describe a file (Entity) that is not inside the bids dataset, and belongs to the software environment. Here the `MNI152_T1_1mm_brain.nii.gz` (MNI152 template) can be considered as a part of FSL ; we use the following IRI for it `"/usr/share/fsl/5.0/data/standard/MNI152_T1_1mm_brain.nii.gz"`. Ideally we would like to create a relation between this Entity and the Environment.

2. We use Nipype's `ExportFile` nodes to export the computed files to the location they belong to in the BIDS tree (if nothing is done, the computed files stay in the workflow working directory). These are Nipype nodes coded in python, and we are therefore not able to write a precise command line as attribute of the corresponding Activities.

3. We refer the software environment as `"bids::prov/#docker.io/nipype/nipype:py38-vavfao8v"` but this could be `docker.io/nipype/nipype:py38` ?

4. We may want to avoid describing temporary files from nipype's working directory (here `bids_prov_workflow/`). For example, we could use blank nodes instead of `"bids::derivatives/bids_prov_workflow/brain_extraction/sub-001_T1w_brain.nii.gz"`.
