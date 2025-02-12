# BIDS Prov example for `dcm2niix`

This example aims at showing provenance traces from a DICOM to Nifti conversion, performed by `dcm2niix` on a Linux-based (Fedora) operating system.

## Overview

This time, we describe the provenance records using BIDS Prov, but inside several *JSON* files.

After conversion, and adding provenance traces, the resulting directory tree looks like this:

```
prov/
├── prov-dcm2niix_act.prov.json
├── prov-dcm2niix_base.prov.json
├── prov-dcm2niix_env.prov.json
└── prov-dcm2niix_soft.prov.json
sourcedata/
sub-02/
└── anat
    ├── sub-02_T1w.json
    └── sub-02_T1w.nii
```

Note that the `sourcedata/` directory contains the source dataset described in the [section hereafter](#source-dataset).

We use:

* the `GeneratedBy` field of JSON sidecar, already existing in the BIDS specification
* modality agnostic files inside the `prov/` directory

## Provenance merge

The python script `code/merge_prov.py` aims at merging all provenance records into one JSON-LD graph.

```shell
pip install bids-prov==0.1.0
mkdir prov/merged/
python code/merge_prov.py
```

## Provenance visualization

We are then able to visualize these provenance files using the following commands (current directory is `examples/dcm2niix_3/`):

```shell
pip install bids-prov==0.1.0
bids_prov_visualizer --input_file prov/merged/prov-dcm2niix.prov.jsonld --output_file prov/merged/prov-dcm2niix.prov.png
```

![](/examples/dcm2niix_3/prov/merged/prov-dcm2niix.prov.png)

## Source dataset

Dataset is the same as the one for [example dcm2niix_1](/BEP028_BIDSprov/examples/dcm2niix_1/README.md#source-dataset).

## Notes

We introduce the following BIDS entity that is currently not existing:
* `prov`
    * Full name: Provenance traces
    * Format: `prov-<label>`
    * Definition: A grouping of provenance traces. Defining multiple provenance traces groups is appropriate when several processings have been performed on data.

We introduce the following BIDS suffixes that are currently not existing:
* `act`: the file describes BIDS Prov `Activities` for the group of provenance traces
* `soft`: the file describes BIDS Prov `Software` for the group of provenance traces
* `env`: the file describes BIDS Prov `Environments` for the group of provenance traces
* `base`: the file describes common BIDS Prov parameters for the group of provenance traces (version and context for BIDS Prov)

We use the `GeneratedBy` field of JSON sidecars to link to `Activities` that created the file the sidecars refers to.

In this example, we rely on the fact that nodes defined in the `prov/*.prov.jsonld` files have `bids::prov/` as base IRIs.

The `code/merge_prov.py` code is responsible for:
* merging the JSON provenance traces into the base JSON-LD graph;
* create an `Entity` and linking it to the `Activity` described by the `GeneratedBy` field in the case of JSON sidecars.

### Limitations

1. The `Environments` term is not defined in the current BIDS Prov context, hence we define environments as `Entities`.

2. Listing all the DICOM files used by the dcm2niix conversion steps would lower readability of the JSON-LD provenance files. Therefore we only listed the following directories as `Entities`:
* `bids::sourcedata/hirni-demo/acq1/dicoms/example-dicom-structural-master/dicoms`

although it is not allowed by the current version of the BIDS Prov specification to have directories as `Entities`.

3. In this example, the provenance for JSON sidecars files is not described.
