# BIDS-Prov example for `heudiconv`

This example aims at showing provenance traces from a DICOM to Nifti conversion, performed by [`heudiconv`](https://heudiconv.readthedocs.io/en/latest/) on a Linux-based (Fedora) operating system.

## Overview

In order to describe provenance records using BIDS Prov, we use:

* the `GeneratedBy` field of JSON sidecar files, already existing in the BIDS specification;
* modality agnostic files inside the `prov/` directory

After conversion and adding provenance traces, the resulting directory tree looks like this:

```
.
├── .bidsignore
├── CHANGES
├── dataset_description.json
├── .heudiconv/
├── participants.json
├── participants.tsv
├── prov/
│   ├── prov-heudiconv_act.prov.json
│   ├── prov-heudiconv_base.prov.json
│   ├── prov-heudiconv_ent.prov.json
│   ├── prov-heudiconv_env.prov.json
│   └── prov-heudiconv_soft.prov.json
├── README
├── scans.json
├── sourcedata/
└── sub-001/
    ├── anat
    │   ├── sub-001_run-1_T1w.json
    │   └── sub-001_run-1_T1w.nii.gz
    ├── sub-001_scans.json
    └── sub-001_scans.tsv
```

Note that the `sourcedata/` directory contains the source dataset described in the [section hereafter](#source-dataset).

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

We are then able to visualize these provenance files using the following commands (current directory is `examples/heudiconv/`):

```shell
pip install bids-prov==0.1.0
bids_prov_visualizer --input_file prov/merged/prov-heudiconv.prov.jsonld --output_file prov/merged/prov-heudiconv.prov.png
```

![](/examples/heudiconv/prov/merged/prov-heudiconv.prov.png)

## Source dataset

We get raw data from https://github.com/psychoinformatics-de/hirni-demo.git, a demo datalad dataset containing dicoms.

```shell
# Get example dicom(s) in a sourcedata/ directory
mkdir sourcedata
cd sourcedata
datalad install --recursive https://github.com/psychoinformatics-de/hirni-demo.git
cd acq1
datalad get ./*
cd ..
ls -1
    acq1
    acq2
    code
    dataset_description.json
    README
    studyspec.json
cd ..
```

Note that we will only convert the anatomical data available in this dataset (`acq1/` directory).

## Perform the conversions

Install `heudiconv`.

```shell
pip install heudiconv==1.3.2
```
With this setup we are ready to convert dicoms to nifti files using `heudiconv`.

Note that we use an already existing heuritic files (`sourcedata/hirni-demo/code/hirni-toolbox/converters/heudiconv/hirni_heuristic.py`). This file needs the `HIRNI_STUDY_SPEC` and `HIRNI_SPEC2BIDS_SUBJECT` environment variables to be set (see the following command lines).

```shell
export HIRNI_STUDY_SPEC=sourcedata/hirni-demo/acq1/studyspec.json
export HIRNI_SPEC2BIDS_SUBJECT=001
heudiconv --files sourcedata/hirni-demo/acq1/dicoms/example-dicom-structural-master/dicoms/*.dcm -o . -f sourcedata/hirni-demo/code/hirni-toolbox/converters/heudiconv/hirni_heuristic.py -s 02 -ss acq1 -c dcm2niix -b --minmeta --overwrite
```

We control that the BIDS dataset has been created and that it contains the nifti files.

```shell
ls -1
    CHANGES
    dataset_description.json
    participants.json
    participants.tsv
    README
    scans.json
    sourcedata/
    sub-001/
    task-oneback_bold.json

tree sub-001/
    sub-001/
    ├── anat
    │   ├── sub-001_run-1_T1w.json
    │   └── sub-001_run-1_T1w.nii.gz
    └── sub-001_scans.tsv
```

## Notes

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

We use the `GeneratedBy` field of JSON sidecars to link to Activities that created the file the sidecars refers to.
We use the `SidecarGeneratedBy` field of JSON sidecars to link to Activities that created or modified the sidecars itself.

In this example, we rely on the fact that nodes defined in the `prov/*.prov.jsonld` files have `bids::prov/` as base IRIs.

## Limitations

1. The `Environments` term is not defined in the current BIDS Prov context, hence we define environments as `Entities`.

2. Listing all the DICOM files used by the heudiconv conversion steps would lower readability of the JSON-LD provenance files. Therefore we only listed the following directories as `Entities`:
* `bids::sourcedata/hirni-demo/acq1/dicoms/example-dicom-structural-master/dicoms`

although it is not allowed by the current version of the BIDS Prov specification to have directories as `Entities`.

3. In this example, the provenance for JSON sidecars files is not described.

4. We used `prov:actedOnBehalfOf` relation between two `Software` objects to describe that `heudiconv` works with internal calls to `dcm2niix`. Although we don't know exactly which parts of the conversion process are done by these two pieces of software. **As a result, we are not able to write the exact command line exectued by dcm2niix**.
