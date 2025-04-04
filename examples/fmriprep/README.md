# A `fMRIPrep` example for BIDS-Prov

This example aims at showing provenance records for the [fMRIPrep](https://fmriprep.org/en/23.1.3/index.html) preprocessing software, as a typical usecase on how to store provenance inside a BIDS derivatives dataset.

> [!NOTE]
> The command lines described in this documentation are supposed to be run from the `examples/fmriprep/` directory.

> [!WARNING]
> This examples needs the bids prov visualizer to export .svg files instead of .png files (for which the resolution is way too low to display a whole fMRIprep graph), hence modifications in `bids_prov/visualize.py`

## Source dataset

We use the dataset from https://openneuro.org/datasets/ds001734/versions/1.0.5, containing raw and preprocessed fMRI data of two versions of the mixed gambles task, from the Neuroimaging Analysis Replication and Prediction Study (NARPS).

```shell
datalad install https://github.com/OpenNeuroDatasets/ds001734.git
git submodule add https://github.com/OpenNeuroDatasets/ds001734.git ds001734
cd ds001734
datalad get sub-001/*
```

## `fMRIPrep` installation

```shell
pip install fmriprep-docker==1.1.4
docker pull poldracklab/fmriprep:1.1.4
mkdir derivatives/
```

## Getting provenance records from nipype

Create a `nipype.cfg` file to setup provenance recording in nipype. The file contains the following lines:
```
[execution]
write_provenance = true
hash_method = content
```

Launch `fMRIPrep` on one subject (sub-001):
```shell
fmriprep-docker --participant-label=001 --fs-license-file=freesurfer_license.txt --config=nipype.cfg -w=derivatives/work/ ds001734/ derivatives/ participant
```

> [!NOTE]
> This is responsible for launching the following command line:
> ```shell
> docker run --rm -it -v <absolute_path_to>/freesurfer_license.txt:/opt/freesurfer/license.txt:ro -v <absolute_path_to>/nipype.cfg:/root/.nipype/nipype.cfg:ro -v <absolute_path_to>ds001734/:/data:ro -v <absolute_path_to>derivatives/:/out -v <absolute_path_to>derivatives/work:/scratch poldracklab/fmriprep:1.1.4 /data /out participant --participant-label=001 -w /scratch
> ```

## Converting nipype provenance to BIDS-Prov

Nipype generates RDF provenance records in Trig format, as contained in `derivatives/fmriprep/prov/nipype/workflow_provenance_20250314T155959.trig`.

We use the `code/convert_prov.py` script to convert it to BIDS-Prov compliant provenance:

```shell
cd derivatives/fmriprep/
python code/convert_prov.py
```

This script perform SPARQL queries to extract a simplified version of the RDF graph, containing activities, entities, environments and agents with these relations:

| Record | relations |
| --- | --- |
| Activities | `Label`<br>`Type`<br>`Command`<br>`AssociatedWith`<br>`Used`<br>`StartedAtTime`<br>`EndedAtTime` |
| Entities | `Label`<br>`AtLocation`<br>`GeneratedBy`<br>`Type`<br>`Digest` |
| Agents | `Label`<br>`Type`<br>`Version` |
| Environments | `Label`<br>`Type`<br>`EnvVar` |

> [!NOTE] The script works with the `code/queries.py` module containing a set of exhaustive queries, and a set of simplified ones. The example uses he simplified queries (that do not extract Environments or Agents) to simplify the output graph.

The script  generates:
* `derivatives/fmriprep/prov/nipype/workflow_provenance_20250314T155959_compacted.jsonld`: a JSON-LD file, which is the serialization of the simplified RDF graph
* `derivatives/fmriprep/prov/nipype/workflow_provenance_20250314T155959_bidsprov.jsonld`: a BIDS-Prov file created by adapting the previous JSON-LD file to a BIDS-Prov skeleton
* provenance records splitted into JSON files `derivatives/fmriprep/prov/prov-fmriprep_*.json`

We are able to visualize the BIDS-Prov graph:
```shell
pip install bids-prov==0.1.0
bids_prov_visualizer --input_file derivatives/fmriprep/prov/nipype/workflow_provenance_20250314T155959_bidsprov.jsonld --output_file derivatives/fmriprep/prov/nipype/workflow_provenance_20250314T155959_bidsprov.svg
```

![](/examples/fmriprep/derivatives/fmriprep/prov/nipype/workflow_provenance_20250314T155959_bidsprov.svg)

## Storing provenance in sidecar JSONs

We use the `code/split_prov.py` script to create (or complement) sidecar JSON files form Entity records of `derivatives/fmriprep/prov/nipype/workflow_provenance_20250314T155959_bidsprov.jsonld`.

```shell
python code/split_prov.py -i prov/nipype/workflow_provenance_20250314T155959_bidsprov.jsonld -o .
```

This gives the following tree (`code/` and `prov/nipype/` directories are ignored):

```
.
├── prov
│   ├── prov-fmriprep_act.json
│   ├── prov-fmriprep_base.json
│   ├── prov-fmriprep_ent.json
│   ├── prov-fmriprep_env.json
│   └── prov-fmriprep_soft.json
└── sub-001
    ├── anat
    │   ├── sub-001_T1w_brainmask.json
    │   ├── sub-001_T1w_brainmask.nii.gz
    │   ├── sub-001_T1w_dtissue.json
    │   ├── sub-001_T1w_dtissue.nii.gz
    │   ├── sub-001_T1w_inflated.L.surf.gii
    │   ├── sub-001_T1w_inflated.L.surf.json
    │   ├── sub-001_T1w_inflated.R.surf.gii
    │   ├── sub-001_T1w_inflated.R.surf.json
    │   ├── sub-001_T1w_label-aparcaseg_roi.json
    │   ├── sub-001_T1w_label-aparcaseg_roi.nii.gz
    │   ├── sub-001_T1w_label-aseg_roi.json
    │   ├── sub-001_T1w_label-aseg_roi.nii.gz
    │   ├── sub-001_T1w_midthickness.L.surf.gii
    │   ├── sub-001_T1w_midthickness.L.surf.json
    │   ├── sub-001_T1w_midthickness.R.surf.gii
    │   ├── sub-001_T1w_midthickness.R.surf.json
    │   ├── sub-001_T1w_pial.L.surf.gii
    │   ├── sub-001_T1w_pial.L.surf.json
    │   ├── sub-001_T1w_pial.R.surf.gii
    │   ├── sub-001_T1w_pial.R.surf.json
    │   ├── sub-001_T1w_preproc.json
    │   ├── sub-001_T1w_preproc.nii.gz
    │   ├── sub-001_T1w_smoothwm.L.surf.gii
    │   ├── sub-001_T1w_smoothwm.L.surf.json
    │   ├── sub-001_T1w_smoothwm.R.surf.gii
    │   ├── sub-001_T1w_smoothwm.R.surf.json
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_brainmask.json
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_brainmask.nii.gz
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_dtissue.json
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_dtissue.nii.gz
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_preproc.json
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_preproc.nii.gz
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_target-T1w_warp.h5
    │   ├── sub-001_T1w_space-MNI152NLin2009cAsym_target-T1w_warp.json
    │   ├── sub-001_T1w_space-orig_target-T1w_affine.json
    │   ├── sub-001_T1w_space-orig_target-T1w_affine.txt
    │   ├── sub-001_T1w_target-fsnative_affine.json
    │   ├── sub-001_T1w_target-fsnative_affine.txt
    │   ├── sub-001_T1w_target-MNI152NLin2009cAsym_warp.h5
    │   └── sub-001_T1w_target-MNI152NLin2009cAsym_warp.json
    └── func
        ├── sub-001_task-MGT_run-01_bold_confounds.json
        ├── sub-001_task-MGT_run-01_bold_confounds.tsv
        ├── sub-001_task-MGT_run-01_bold_space-fsaverage5.L.func.gii
        ├── sub-001_task-MGT_run-01_bold_space-fsaverage5.L.func.json
        ├── sub-001_task-MGT_run-01_bold_space-fsaverage5.R.func.gii
        ├── sub-001_task-MGT_run-01_bold_space-fsaverage5.R.func.json
        ├── sub-001_task-MGT_run-01_bold_space-MNI152NLin2009cAsym_brainmask.json
        ├── sub-001_task-MGT_run-01_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz
        ├── sub-001_task-MGT_run-01_bold_space-MNI152NLin2009cAsym_preproc.json
        ├── sub-001_task-MGT_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz
        ├── sub-001_task-MGT_run-01_bold_space-T1w_label-aparcaseg_roi.json
        ├── sub-001_task-MGT_run-01_bold_space-T1w_label-aparcaseg_roi.nii.gz
        ├── sub-001_task-MGT_run-01_bold_space-T1w_label-aseg_roi.json
        ├── sub-001_task-MGT_run-01_bold_space-T1w_label-aseg_roi.nii.gz
        ├── sub-001_task-MGT_run-02_bold_confounds.json
        ├── sub-001_task-MGT_run-02_bold_confounds.tsv
        ├── sub-001_task-MGT_run-02_bold_space-fsaverage5.L.func.gii
        ├── sub-001_task-MGT_run-02_bold_space-fsaverage5.L.func.json
        ├── sub-001_task-MGT_run-02_bold_space-fsaverage5.R.func.gii
        ├── sub-001_task-MGT_run-02_bold_space-fsaverage5.R.func.json
        ├── sub-001_task-MGT_run-02_bold_space-MNI152NLin2009cAsym_brainmask.json
        ├── sub-001_task-MGT_run-02_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz
        ├── sub-001_task-MGT_run-02_bold_space-MNI152NLin2009cAsym_preproc.json
        ├── sub-001_task-MGT_run-02_bold_space-MNI152NLin2009cAsym_preproc.nii.gz
        ├── sub-001_task-MGT_run-02_bold_space-T1w_label-aparcaseg_roi.json
        ├── sub-001_task-MGT_run-02_bold_space-T1w_label-aparcaseg_roi.nii.gz
        ├── sub-001_task-MGT_run-02_bold_space-T1w_label-aseg_roi.json
        ├── sub-001_task-MGT_run-02_bold_space-T1w_label-aseg_roi.nii.gz
        ├── sub-001_task-MGT_run-03_bold_confounds.json
        ├── sub-001_task-MGT_run-03_bold_confounds.tsv
        ├── sub-001_task-MGT_run-03_bold_space-fsaverage5.L.func.gii
        ├── sub-001_task-MGT_run-03_bold_space-fsaverage5.L.func.json
        ├── sub-001_task-MGT_run-03_bold_space-fsaverage5.R.func.gii
        ├── sub-001_task-MGT_run-03_bold_space-fsaverage5.R.func.json
        ├── sub-001_task-MGT_run-03_bold_space-MNI152NLin2009cAsym_brainmask.json
        ├── sub-001_task-MGT_run-03_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz
        ├── sub-001_task-MGT_run-03_bold_space-MNI152NLin2009cAsym_preproc.json
        ├── sub-001_task-MGT_run-03_bold_space-MNI152NLin2009cAsym_preproc.nii.gz
        ├── sub-001_task-MGT_run-03_bold_space-T1w_label-aparcaseg_roi.json
        ├── sub-001_task-MGT_run-03_bold_space-T1w_label-aparcaseg_roi.nii.gz
        ├── sub-001_task-MGT_run-03_bold_space-T1w_label-aseg_roi.json
        ├── sub-001_task-MGT_run-03_bold_space-T1w_label-aseg_roi.nii.gz
        ├── sub-001_task-MGT_run-04_bold_confounds.json
        ├── sub-001_task-MGT_run-04_bold_confounds.tsv
        ├── sub-001_task-MGT_run-04_bold_space-fsaverage5.L.func.gii
        ├── sub-001_task-MGT_run-04_bold_space-fsaverage5.L.func.json
        ├── sub-001_task-MGT_run-04_bold_space-fsaverage5.R.func.gii
        ├── sub-001_task-MGT_run-04_bold_space-fsaverage5.R.func.json
        ├── sub-001_task-MGT_run-04_bold_space-MNI152NLin2009cAsym_brainmask.json
        ├── sub-001_task-MGT_run-04_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz
        ├── sub-001_task-MGT_run-04_bold_space-MNI152NLin2009cAsym_preproc.json
        ├── sub-001_task-MGT_run-04_bold_space-MNI152NLin2009cAsym_preproc.nii.gz
        ├── sub-001_task-MGT_run-04_bold_space-T1w_label-aparcaseg_roi.json
        ├── sub-001_task-MGT_run-04_bold_space-T1w_label-aparcaseg_roi.nii.gz
        ├── sub-001_task-MGT_run-04_bold_space-T1w_label-aseg_roi.json
        └── sub-001_task-MGT_run-04_bold_space-T1w_label-aseg_roi.nii.gz
```

### Limitations

* For now, we use a simplified description of the provenance, leaving aside software and environments as well as keys such as `Digest`, `Version`, `EnvVar`, `StartedAtTime`, `EndedAtTime`.
* Some entities end up with several labels / atlocation. E.g.:
```JSON-LD
{
    "Id": "http://iri.nidash.org/262c247816c9fc071309a1da8bad277d",
    "Type": "Entities",
    "Label": [
      "file://b330d9dac87a/scratch/fmriprep_wf/single_subject_001_wf/func_preproc_task_MGT_run_03_wf/sdc_wf/phdiff_wf/demean/sub-001_phasediff_rads_unwrapped_filt_demean.nii.gz",
      "file://b330d9dac87a/scratch/fmriprep_wf/single_subject_001_wf/func_preproc_task_MGT_run_02_wf/sdc_wf/phdiff_wf/demean/sub-001_phasediff_rads_unwrapped_filt_demean.nii.gz"
    ],
    "Atlocation": [
      "file://b330d9dac87a/scratch/fmriprep_wf/single_subject_001_wf/func_preproc_task_MGT_run_03_wf/sdc_wf/phdiff_wf/demean/sub-001_phasediff_rads_unwrapped_filt_demean.nii.gz",
      "file://b330d9dac87a/scratch/fmriprep_wf/single_subject_001_wf/func_preproc_task_MGT_run_02_wf/sdc_wf/phdiff_wf/demean/sub-001_phasediff_rads_unwrapped_filt_demean.nii.gz"
    ],
    "https://github.com/bids-standard/BEP028_BIDSprov/terms/Digest": "sha512:c585500ee6565b5e8277e3cf72dcdef81768439e7998c258d9e3cfc4042cf2d3fa80ecd359400deda90a4ed141e3180b78a942b32827bd41fb0ca367c8f91c9c"
}
```
* As a result of the previous point, we are not able to fully replace these Entities from the `prov/prov-fmriprep_ent.json` file by a `GeneratedBy` field inside a sidecar JSON
* Some terms are missing in the BIDS-Prov context although they are in the specification (such as `Digest`, `Version`, `EnvVar`)
* For now, the conversion script is not able to transform RDF triplets into dictionaries, as requested for `Digest` or `EnvVar` objects.
* IRIs are not human readable enough (e.g.: `http://iri.nidash.org/262c247816c9fc071309a1da8bad277d`)
* Some "Function" and other activity nodes Use and Generate the same entity. Does this really mean that they read and write the same file ?

### Next steps

* how to represent entities with two labels and locations ?
* then, use file names for Ids of entities
* make extractions based on consistent use of qualifiedUsage and qualifiedGeneration (vs. Used and GeneratedBy)
* investiate activities Using an Generating the same file (e.g.: `http://iri.nidash.org/4650c7ac00df11f0992d72ca464e997e` with entity `http://iri.nidash.org/72737575a38dda35b8ab6530a55aa543` which is `file://b330d9dac87a/data/sub-001/anat/sub-001_T1w.nii.gz`)
