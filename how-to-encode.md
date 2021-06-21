## How to encode my workflow given the BIDS-prov ontology ?

Either you are a software developper, a researcher striving for reproducible science, or anyone working in the neuro-imaging field and willing to 
use BIDS-prov, at some point you might be asking yourself the following question :

> What is the right way to represent my workflow in the philosophy of BIDS-prov ?

This set of examples will give you an overview the the typical cases and how to apply BIDS-prov concepts !

Notes
-----
We only show pieces of the `records` field of the provenance file for each case. The context for these pieces is fixed, and can be found [here](https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json)

------------

### One of my steps makes use of a docker container, of what type should it be ? What relations to represent ?

An example of this can is [fMRIPrep](https://fmriprep.org/en/stable/index.html), which can be launched as a docker container.

The most simplistic way you can think of is to have this container "black-boxed" in your workflow. You basically record the calling of this container (`command` section) and the output (see the [outputs section from fMRIPrep](https://fmriprep.org/en/stable/outputs.html))

```json
    "prov:Activty": [
      {
        "@id": "niiri:fMRIPrep1",
        "label": "fMRIPrep step",
        "command": "fmriprep data/bids_root/ out/ participant -w work/",
        "parameters": {
            "bids_dir" : "data/bids_root",
            "output_dir" : "out/",
            "anaysis_level" : "participant"
        },
        "wasAssociatedWith": "RRID:SCR_016216",
        "startedAtTime": "2020-10-10T10:00:00",
        "used": "niiri:bids_data1"
      },
    ]
    "prov:Entity": [
      {
        "@id": "niiri:bids_data1",
        "label": "Bids dataset 1",
        "prov:atLocation": "data/bids_root",
        "generatedAt": "2019-10-10T10:00:00"
      },
    {
        "@id": "niiri:fmri_prep_output1",
        "label": "FMRI prep output 1",
        "prov:atLocation": "out/",
        "generatedAt": "2019-10-10T10:00:00",
        "wasGeneratedBy": "niiri:fMRIPrep1"
    },
    ]
```

--------------

### I have a group of task, belonging to a subgroup of task ?
You can the `prov-O` isPartOf relationship to add an extralink to you activity
```json
    "prov:Activty": [
      {
        "@id": "niiri:activity_group1",
        "label": "Activity Group 1",
        "command": "launch.sh"
      },
      {
        "@id": "niiri:activity_1",
        "label": "Activity 1",
        "command": "task_specific_executable.sh --arg 1",
        "parameters": {
            "arg1" : 1
        },
        "wasAssociatedWith": "RRID:SCR_007037",
        "startedAtTime": "2019-10-10T10:00:00",
        "endedAtTime": "2019-10-10T10:00:00",
        "used": "niiri:entity_1"
      }
    ]
    "prov:Entity": [
      {
        "@id": "niiri:entity_1",
        "label": "Entity 1",
        "prov:atLocation": "/root/file.xyz",
        "generatedAt": "2019-10-10T10:00:00"
      },
    ]
```

You can see relations with objects of other types (entites here) are reserved to the activity with the lowest level :`Activity 1`

`Activity Group 1` is just here to express a hierarchy.

