# A `fMRIPrep` example for BIDS-Prov

This example aims at showing provenance traces for the [fMRIPrep](https://fmriprep.org/en/23.1.3/index.html) preprocessing software on a Linux-based (Fedora) operating system.

## `fMRIPrep` installation

```shell
pip install fmriprep-docker==1.1.4

docker pull poldracklab/fmriprep:1.1.4

mkdir derivatives/
```

Launching `fMRIPrep` on one subject.

```shell
fmriprep-docker --participant-label=001 --fs-license-file=soft/freesurfer/license.txt --config=nipype.cfg -w=data/ds001734_fmriprep/work/ dev/BEP028_BIDSprov/examples/fmriprep/ds001734/ data/ds001734_fmriprep/ participant 
```

TODO : alternative nipype configuration to enable provenance

nipype.cfg:
```
[execution]
write_provenance = true
hash_method = content
```

docker run --rm -it -v /home/$USER/soft/freesurfer/license.txt:/opt/freesurfer/license.txt:ro -v /home/$USER/dev/bidsprov/nipype.cfg:/root/.nipype/nipype.cfg:ro -v /home/$USER/nas-empenn/share/dbs/narps_open/data/original/ds001734/:/data:ro -v /data/$USER/ds001734_fmriprep:/out -v /data/$USER/ds001734_fmriprep/work:/scratch poldracklab/fmriprep:1.1.4 /data /out participant --participant-label=001 -w /scratch



## Source dataset

We use the dataset from https://openneuro.org/datasets/ds001734/versions/1.0.5, containing raw and preprocessed fMRI data of two versions of the mixed gambles task, from the Neuroimaging Analysis Replication and Prediction Study (NARPS).

```shell
datalad install https://github.com/OpenNeuroDatasets/ds001734.git

git submodule add https://github.com/OpenNeuroDatasets/ds001734.git  examples/fmriprep/ds001734

datalad get sub-001/*
```

## Associated provenance

In order to describe provenance records using BIDS Prov, we use:

* modality agnostic files inside the `prov/` directory
* subject / modality level provenance files

```
.
├── code
│   └── merge_prov.py
├── prov
│   ├── merged
│   │   ├── prov-fmriprep.prov.jsonld
│   │   └── prov-fmriprep.prov.png
│   ├── prov-fmriprep_base.prov.json
│   ├── prov-fmriprep_ent.prov.json
│   ├── prov-fmriprep_env.prov.json
│   └── prov-fmriprep_soft.prov.json
└── sub-001
    ├── anat
    │   ├── sub-001_T1w_prov-fmriprep_act.prov.json
    │   └── sub-001_T1w_prov-fmriprep_ent.prov.json
    └── func
        ├── sub-001_task-MGT_bold_prov-fmriprep_act.prov.json
        └── sub-001_task-MGT_bold_prov-fmriprep_ent.prov.json
```

## New features for BIDS / BIDS Prov

We introduce the following BIDS entity that is currently not existing:

* `prov`
    * Full name: Provenance traces
    * Format: `prov-<label>`
    * Definition: A grouping of provenance traces. Defining multiple provenance traces groups is appropriate when several processings have been performed on data.

We introduce the following BIDS suffixes that are currently not existing:

* `act`: the file describes BIDS Prov Activities for the group of provenance traces
* `soft`: the file describes BIDS Prov Software for the group of provenance traces
* `env`: the file describes BIDS Prov Environments for the group of provenance traces
* `ent`: the file describes BIDS Prov Entities for the group of provenance traces
* `base`: the file describes common BIDS Prov parameters for the group of provenance traces (version and context for BIDS Prov)

## Merging JSON in a JSON-LD file and plotting graph

The python script `code/merge_prov.py` aims at merging all these provenance records into one JSON-LD graph.

```shell
mkdir prov/merged/
python code/merge_prov.py
```

From that, we generate the JSON-LD graph `prov/merge/prov-fmriprep.prov.jsonld`. Then we were able to plot the graph as a png file. We used this command:

```shell
pip install bids-prov==0.1.0
bids_prov_visualizer --input_file prov/merged/prov-fmriprep.prov.jsonld --output_file prov/merged/prov-fmriprep.prov.png
```

![](/examples/fmriprep/prov/merged/prov-fmriprep.prov.png)

### Notes

In this example, we rely on the fact that nodes defined in the `prov/*.prov.jsonld` files have `bids::prov/` as base IRIs.

### Limitations
