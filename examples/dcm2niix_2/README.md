# BIDS Prov example #2 for `dcm2niix`

This example aims at showing provenance traces from a DICOM to Nifti conversion, performed by `dcm2niix` on a Linux-based (Fedora) operating system.

## Overview

We use JSON-LD sidecars and modality agnostic files inside the `prov/` directory to store all provenance traces.

After conversion, and adding provenance traces, the resulting directory tree looks like this:

```
prov/
├── environments.prov.jsonld
└── software.prov.jsonld
sourcedata/
sub-02/
└── anat
    ├── sub-02_T1w.json
    ├── sub-02_T1w.nii
    └── sub-02_T1w.prov.jsonld
```

Note that the `sourcedata/` directory contains the source dataset described in the [section hereafter](#source-dataset).

* `sub-02_T1w.prov.jsonld` is a "sidecars" defining provenance for the corresponding `.nii` file.
* `environments.prov.jsonld` mutualises the declaration of software environments objects for lower level prov files
* `software.prov.jsonld` mutualises the declaration of software pieces objects for lower level prov files

## Provenance merge

The python script `code/merge_prov.py` aims at merging all provenance records into one JSON-LD graph.

```shell
pip install bids-prov==0.1.0
mkdir prov/merged/
python code/merge_prov.py
```

## Provenance visualization

We are then able to visualize these provenance files using the following commands (current directory is `examples/dcm2niix_2/`):

```shell
pip install bids-prov==0.1.0
    bids_prov_visualizer --input_file prov/merged/dcm2niix.prov.jsonld --output_file prov/merged/dcm2niix.prov.png
```

![](/examples/dcm2niix_2/prov/merged/dcm2niix.prov.png)

## Source dataset

Dataset is the same as the one for [example dcm2niix_1](/BEP028_BIDSprov/examples/dcm2niix_1/README.md#source-dataset).

### Notes

In this example, we rely on the fact that nodes defined in the `prov/*.prov.jsonld` files have `bids::prov/` as base IRIs. Here are the involved nodes:
* `bids::prov/#dcm2niix-xce5m9z3`
* `bids::prov/#fedora-b7hmkmqd`

### Limitations

The `bids::prov/f#edora-b7hmkmqd` node defined in `prov/environments.prov.jsonld` is defined as an `Entity` as the current context (commit [ce0eb77](https://github.com/bids-standard/BEP028_BIDSprov/commit/ce0eb774abd9527e594bd69212a87d5047864678)) does not define the `Environments` term.

Listing all the DICOM files used by the dcm2niix conversion steps would lower readability of the JSON-LD provenance files. Therefore we only listed the following directories as `Entities`:
* `bids::sourcedata/hirni-demo/acq1/dicoms/example-dicom-structural-master/dicoms`
* `bids::sourcedata/hirni-demo/acq2/dicoms/example-dicom-functional-master/dicoms`

although it is not allowed by the current version of the BIDS Prov specification to have directories as `Entities`.
