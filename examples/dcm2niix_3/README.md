# BIDS Prov example for `dcm2niix`

This example aims at showing the capture of provenance for a [`dcm2niix`](https://github.com/rordenlab/dcm2niix) usecase: converting DICOM data to Nifti files within a BIDS dataset.

Source data for this example can be found here: https://github.com/psychoinformatics-de/hirni-demo. This is a datalad dataset containing anatomical and functional MRI acquisitions. The contents of this dataset can be downloaded using:

```shell
mkdir sourcedata
cd sourcedata
datalad install --recursive https://github.com/psychoinformatics-de/hirni-demo.git
```

> [!NOTE] Note that the dataset must be added inside the `sourcedata/` directory.

## Purpose

The aim of the example is to describe the provenance records using BIDS Prov, but inside several *JSON* files.
We use:

* the `GeneratedBy` field of JSON sidecars, already existing in the BIDS specification
* modality agnostic files inside the `prov/` directory

as follows:

```
.
├── prov
│   ├── prov-dcm2niix_act.prov.json
│   ├── prov-dcm2niix_base.prov.json
│   ├── prov-dcm2niix_env.prov.json
│   └── prov-dcm2niix_soft.prov.json
└── sub-02
    ├── ses-20130717141500
    │   └── anat
    │       └── sub-02_ses-20130717141500_T1w.json
    └── ses-20140425155335
        └── func
            └── sub-02_ses-20140425155335_task-oneback_run-1_bold.json
```

## New features for BIDS / BIDS Prov

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

## Merging JSON in a JSON-LD file and plotting graph

The python script `code/merge_prov.py` aims at merging all these provenance records into one JSON-LD graph.

```shell
mkdir prov/merged/
python code/merge_prov.py
```

From that, we generate the JSON-LD graph `prov/merge/prov-dcm2niix.prov.jsonld`. Then we were able to plot the graph as a png file. We used this command:

```shell
pip install bids-prov==0.1.0
bids_prov_visualizer --input_file prov/merged/prov-dcm2niix.prov.jsonld --output_file prov/merged/prov-dcm2niix.prov.png
```

![](/examples/dcm2niix/prov/merged/prov-dcm2niix.prov.png)

### Notes

In this example, we rely on the fact that nodes defined in the `prov/*.prov.jsonld` files have `bids::prov/` as base IRIs.

The `code/merge_prov.py` code is responsible for:
* merging the JSON provenance traces into the base JSON-LD graph;
* create an `Entity` and linking it to the `Activity` described by the `GeneratedBy` field in the case of JSON sidecars.

### Limitations

1. The `Environments` term is not defined in the current BIDS Prov context, hence we define environments as `Entities`.

2. Listing all the DICOM files used by the dcm2niix conversion steps would lower readability of the JSON-LD provenance files. Therefore we only listed the following directories as `Entities`:
* `bids::sourcedata/hirni-demo/acq1/dicoms/example-dicom-structural-master/dicoms`
* `bids::sourcedata/hirni-demo/acq2/dicoms/example-dicom-functional-master/dicoms`

although it is not allowed by the current version of the BIDS Prov specification to have directories as `Entities`.

3. In this example, the provenance for JSON sidecars files is not described.
