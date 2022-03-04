## BIDS Extension Proposal 28 (BEP028): Provenance
*version 0.0.1 (draft) - Available under the CC-BY 4.0 International license.*

*Extension moderators/leads: Satra Ghosh &lt;[satra@mit.edu](mailto:satra@mit.edu)> and Camille Maumet &lt;[camille.maumet@inria.fr](mailto:camille.maumet@inria.fr)>*

*Contributors: Stefan Appelhoff, Chris Markiewicz, Yaroslav Halchenko, Jean-Baptiste Poline,  Rémi Adon, Michael Dayan, Sarah Saneei, Eric Earl, Tibor Auer.*

We meet every two weeks by videoconference on Mondays at 7-8am PDT / 10am-11am EDT / 3-4pm BST. The group is always open to new contributors interested in neuroimaging data sharing. To join the call or to ask any question, please email us at [incf-nidash-nidm@googlegroups.com](mailto:incf-nidash-nidm@googlegroups.com).


---
This document contains a draft of the Brain Imaging Data Structure standard extension. It is a community effort to define standards in data / metadata. This is a working document in draft stage and any comments are welcome. 

This specification is an extension of BIDS, and general principles are shared. The specification should work for many different settings and facilitate the integration with other imaging methods.

To see the original BIDS specification, see this link. This document inherits all components of the original specification (e.g. how to store imaging data, events, stimuli and behavioral data), and should be seen as an extension of it, not a replacement.

---



## Table of contents
[TOC]

## 1. Overview {#1-overview}


### 1.1 Goals {#1-1-goals}

Interpreting and comparing scientific results and enabling reusable data and analysis output require understanding provenance, i.e. how the data were generated and processed. To be useful, the provenance must be comprehensive, understandable, easily communicated, and captured automatically in machine accessible form. Provenance records are thus used to encode transformations between digital objects.

This specification is aimed at describing the provenance of a BIDS dataset. This description is retrospective, i.e. it describes a set of steps that were executed in order to obtain the dataset (this is different from prospective descriptions of workflows that could for instance list all sets of steps that can be run on this dataset).


### 1.2 Which type of provenance is covered in this BEP? {#1-2-which-type-of-provenance-is-covered-in-this-bep}

Provenance comes up in many different contexts in BIDS. This specification focuses on representing the processings that were applied to a dataset. These could be for instance:



1. The raw conversion from DICOM images or other instrument native formats to BIDS layout, details of stimulus presentation and cognitive paradigms, and clinical and neuropsychiatric assessments, each come with their own details of provenance.
2. In BIDS derivatives, the consideration of outputs requires knowledge of which inputs from the BIDS dataset were used together with what software was run in what environment and with what parameters.

But provenance comes up in other contexts as well, which might be addressed at a later stage:



3. For datasets and derivatives, provenance can also include details of why the data were collected in the first place covering hypotheses, claims, and prior publications. Provenance can encode support for which claims were supported by future analyses.
4. Provenance can involve information about people and institutions involved in a study.
5. Provenance records can highlight reuse of datasets while providing appropriate attribution to the original dataset generators as well as future transformers.  

Provenance can be captured using different mechanisms, but independent of encoding, always reflects transformations by either humans or software. The interpretability of provenance records requires a consistent vocabulary for provenance as well as an expectation for a consistent terminology for the objects being encoded. 

Note that some level of provenance is already encoded in BIDS (cf. ), this BEP avoids duplicating information already available in sidecar JSONs.


### 1.3 File naming {#1-3-file-naming}

This document describes the contents of a BIDS Prov file; for naming and organization conventions, please consult the [BIDS specification]([https://bids-specification.readthedocs.io](https://bids-specification.readthedocs.io)). Until these conventions are established in BIDS, it is RECOMMENDED to use the following:

BIDS-Prov files are JSON-LD files --, i.e. a specific type of JSON files that allows encoding graph-like structures with the Resource Description Framework[^1] --  

They can be stored in two different locations:

**File level provenance.** BIDS-Prov files can be stored immediately alongside the BIDS file (or BIDS-Derivatives file) they apply to. Each BIDS-Prov file must meet the following naming convention:


```
[pipeline<id>/]
    sub-<label>/
        [ses-<label>/]
            <modality>/
                <file-name>_prov.jsonld
```


At the file level, provenance follows some of the same concepts at the dataset level, but is specifically about the current file under consideration.


**Dataset level provenance.** BIDS-Prov files can be stored in a `prov/` directory immediately below the BIDS dataset (or BIDS-Derivatives dataset) root. Each BIDS-Prov file must meet the following naming convention:


```
prov/
    [<subfolders>*/]
        <label>_prov.jsonld
```


At the dataset level, provenance could be about the dataset itself, or about any BIDS file in the dataset. 

Dataset level provenance may evolve as new data are added, which may include sourcedata, BIDS data, and BIDS derived data. 


### 1.2 Top-level structure {#1-2-top-level-structure}


#### File-level provenance

A skeleton for a file-level BIDS-Prov JSON-LD file looks like this:


```
{
"@context": "https://purl.org/nidash/bidsprov/context.json", 
"BIDSProvVersion": "1.0.0", 
<...Entity 1...>
"wasGeneratedBy": {
<...Activity...>
    "wasAssociatedWith": {
        <...Agent...>
        },
    "used": {
        <...Entity 2…>
      }
    }
}
```

<table>
  <tr>
   <td>


<strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>@context</code>
   </td>
   <td>REQUIRED. A URL to the BIDS-Prov json context. Value must be “<code>https://purl.org/nidash/bidsprov/context.json"</code>
   </td>
  </tr>
  <tr>
   <td><code>BIDSProvVersion</code>
   </td>
   <td>REQUIRED. A string identifying the version of the specification adhered to.
   </td>
  </tr>
  <tr>
   <td><code>[no-key : root-level attributes]</code>
   </td>
   <td>REQUIRED. An Entity record describing the provenance (see “Entity” section below).
   </td>
  </tr>
  <tr>
   <td><code>wasGeneratedBy</code>
   </td>
   <td>REQUIRED. An Activity describing the provenance (see “Activity”, section below).
   </td>
  </tr>
  <tr>
   <td><code>wasAssociatedWith</code>
   </td>
   <td>OPTIONAL. An Agent describing the provenance (see “Activity”, section below).
   </td>
  </tr>
  <tr>
   <td><code>used</code>
   </td>
   <td>OPTIONAL. An Entity describing the provenance (see “Entity”, section below).
   </td>
  </tr>
</table>



#### Dataset-level provenance

A skeleton for a dataset level BIDS-Prov JSON-LD file looks like this:


```
{
"@context": "https://purl.org/nidash/bidsprov/context.json",  
"BIDSProvVersion": "0.0.1",
"records": {
  "Agent": [
    {
        <...Agent 1...>
    },
    {
        <...Agent 2...>
    }
  ],
  "Activity": [
  {
        <...Activity 1...>
        <used>
        <generated>
        <wasAssociatedWith>
  }
  {
        <...Activity 2...>
  }
  ],
  "Entity": [
  {
        <...Entity 1...>
        <wasDerivedFrom>
        <wasAttributedTo>
  },
  {
        <...Entity 2...>
  }
  ]
  }
}
}
```

<table>
  <tr>
   <td>

<strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>@context</code>
   </td>
   <td>REQUIRED. A URL to the BIDS-Prov json context. Value must be “<code>https://purl.org/nidash/bidsprov/context.json"</code>
   </td>
  </tr>
  <tr>
   <td><code>BIDSProvVersion</code>
   </td>
   <td>REQUIRED. A string identifying the version of the specification adhered to.
   </td>
  </tr>
  <tr>
   <td><code>records</code>
   </td>
   <td>REQUIRED. A list of Activity, Entity and Agent records describing the provenance (see “Activity”, “Entity” and “Agent” sections below).
   </td>
  </tr>
</table>


A complete schema for the model file to facilitate specification and validation is available from [https://github.com/bids-standard/BEP028_BIDSprov](https://github.com/bids-standard/BEP028_BIDSprov). In the event of disagreements between the schema and the specification, the specification is authoritative.


## 2. Provenance records {#2-provenance-records}

Each provenance record is composed of a set of Activities that represent the transformations that have been applied to the data. Each Activity can use Entities as inputs and outputs. The Agent specifies the software package.


### 2.1 Activity {#2-1-activity}

Each Activity record has the following fields:


<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>@id</code>
   </td>
   <td>REQUIRED. A UUID/URN. An (randomly-assigned) identifier for the activity.
   </td>
  </tr>
  <tr>
   <td><code>label</code>
   </td>
   <td>REQUIRED. String. Name of the tool used (e.g. “bet”).
   </td>
  </tr>
  <tr>
   <td><code>command</code>
   </td>
   <td>REQUIRED. String. Command used to run the tool.
   </td>
  </tr>
  <tr>
   <td><code>parameters</code>
   </td>
   <td>OPTIONAL. Dict. A dictionary defining the parameters as key-value pairs.
   </td>
  </tr>
  <tr>
   <td><code>wasAssociatedWith</code>
   </td>
   <td>OPTIONAL. UUID. Identifier of the software package used to compute this activity (the corresponding Agent must be defined with its own Agent record).
   </td>
  </tr>
  <tr>
   <td><code>used</code>
   </td>
   <td>OPTIONAL. UUID. Identifier of an entity used by this activity (the corresponding Entity must be defined with its own Entity record).
   </td>
  </tr>
  <tr>
   <td><code>type</code>
   </td>
   <td>OPTIONAL. URI. A term from a controlled vocabulary that more specifically describes the activity.
   </td>
  </tr>
  <tr>
   <td><code>startedAtTime</code>
   </td>
   <td>OPTIONAL. xsd:<em>dateTime. </em>A timestamp tracking the start when this activity started
   </td>
  </tr>
</table>



### 2.2 Entity {#2-2-entity}

Each Entity (as a record or a top-level entity) has the following fields:


<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>@id</code>
   </td>
   <td>OPTIONAL. UUID. An (randomly-assigned) identifier for the entity.
   </td>
  </tr>
  <tr>
   <td><code>label</code>
   </td>
   <td>REQUIRED. String. A name for the entity.
   </td>
  </tr>
  <tr>
   <td><code>atLocation</code>
   </td>
   <td>OPTIONAL. String. For input files, this is the relative path to the file on disk.
   </td>
  </tr>
  <tr>
   <td><code>wasGeneratedBy</code>
   </td>
   <td>OPTIONAL. UUID. Identifier of the activity which generated this entity (the corresponding Activity must be defined with its own Activty record).
   </td>
  </tr>
  <tr>
   <td><code>type</code>
   </td>
   <td>OPTIONAL. URI. A term from a controlled vocabulary that more specifically describes the activity.
   </td>
  </tr>
</table>



### 2.3 Agent (Optional) {#2-3-agent-optional}

Including an Agent record is OPTIONAL. If included, each Agent record has the following fields:


<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>@id</code>
   </td>
   <td>REQUIRED. UUID. An (randomly-assigned) identifier for the software (this identifier will be used to associated activities with this software).
   </td>
  </tr>
  <tr>
   <td><code>rrid</code>
   </td>
   <td>OPTIONAL. URI. URI of the RRID for this software package (cf. <a href="https://scicrunch.org/resources/about/Getting%20Started">scicrunch</a>).
   </td>
  </tr>
  <tr>
   <td><code>label</code>
   </td>
   <td>REQUIRED. String. Name of the software.
   </td>
  </tr>
  <tr>
   <td><code>version</code>
   </td>
   <td>REQUIRED. String. Version of the software.
   </td>
  </tr>
</table>



### 2.4 Environments (Optional) {#2-4-environments-optional}

Information about the environment in which the provenance record was obtained is modeled with an environment record. 

Environment records are OPTIONAL. If included, each environment record MUST have the following fields:


<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>@id</code>
   </td>
   <td>REQUIRED. UUID. A (randomly-assigned) identifier for the environment (this identifier will be used to associated activities with this environment).
   </td>
  </tr>
  <tr>
   <td><code>label</code>
   </td>
   <td>REQUIRED. String. Name of the software.
   </td>
  </tr>
  <tr>
   <td><code>env_vars</code>
   </td>
   <td>OPTIONAL. Dict. A dictionary defining the environment variables as key-value pairs. 
   </td>
  </tr>
  <tr>
   <td><code>...</code>
   </td>
   <td>
   </td>
  </tr>
</table>



## 4 Positioning with respect to other BIDS models {#4-positioning-with-respect-to-other-bids-models}


### 4.1 Provenance in BIDS derivatives {#4-1-provenance-in-bids-derivatives}

Comments/things to discuss/incorporate: 



* Yarik: we should position BIDS-Prov w.r.t. Other provenance info available in BIDS derivatives
* JB: Question on how to organize info in BIDS-Prov versus what will be available in bids-derivative sidecars


### 4.2 Justification for Separating Provenance from file JSON {#4-2-justification-for-separating-provenance-from-file-json}

Provenance is information about a file, including any metadata that is relevant to the file itself. Thus any BIDS data file and its associated JSON sidecar metadata together constitute a unique entity. As such, one may want to record the provenance of the JSON file as much as the provenance of the BIDS file. In addition, separating the provenance as a separate file for now, allows this to be an OPTIONAL component, and by encoding provenance as a JSON-LD document allows capturing the provenance as an individual record or multiple records distributed throughout the dataset.


## 5 Graph model {#5-graph-model}


## 6 How to encode your workflow with BIDS-prov


## Either you are a software developer, a researcher striving for reproducible science, or anyone working in the neuroimaging field and willing to use BIDS-prov, at some point you might be asking yourself the following question : What is the right way to represent my workflow in the philosophy of BIDS-prov ?


## This set of examples will give you an overview of the typical cases and how to apply BIDS-prov concepts !

                
                
TODO: the examples of provenance covered by the spec and descripbed in "Goal" should be covered with their own example here

#### I have many activities/entities to track, should I put everything in a single file ?

Simple answer : NO. BIDS-prov has been designed for provenance records to be shared across multiple files

If you have Activity 1 and Entity 1 defined in a provenance file called init.json, this file can look like the following

"prov:Activity": [

    {


          "@id": "niiri:init",


          "label": "Do some init",


          "command": "python -m my_module.init --weights '[0, 1]'",


          "parameters": { "weights" : [0, 1]},


          "startedAtTime": "2020-10-10T10:00:00",


          "used": "niiri:bids_data1"

    },

],

"prov:Entity": [

    {"@id": "niiri:bids_data1", "label": "Bids dataset 1", "prov:atLocation": "data/bids_root"}

]

Now if we want `Entity 2` defined in `preproc.json` to also have a "wasGeneratedBy" field referencing "Activity 1" from `init.json`, we can simply write the following

"prov:Entity": [

     {"@id": "niiri:bids_data1", "label": "Bids dataset 1", "wasGeneratedBy": "niiri:init"}

]

Needless to say, both `init.json` and `preproc.json` must have the reference the same context file (in a "@context" field at the very top)


#### I want to track provenance for subject-level analysis, should I declare a prov file per subject ?

You can create a single prov file for every subject. Yet another option is to use globbing to group multiple files into the same entity, using globbing in the `generatedAt` field of this entity.

Files for different subjects usually share common prefixes and extensions.

"prov:Entity": [

   {"@id": "niiri:hfdhbfd", "label": "anat raw files", "prov:atLocation": "sub-*/anat/sub-*_T1w.nii.gz"},

   {"@id": "niiri:fdhbfd", "label": "func raw files", "prov:atLocation": "sub-*/func/sub-*_task-tonecounting_bold.nii.gz"}

]


#### One of my steps makes use of a docker container, of what type should it be ? What relations to represent ?

An example of this can be [fMRIPrep](https://fmriprep.org/en/stable/index.html), which can be launched as a docker container.

The most simplistic way you can think of is to have this container "black-boxed" in your workflow. You basically record the calling of this container (`command` section) and the output (see the outputs section from fMRIPrep)

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


          "used": "niiri:bids_data1"

    },

  ],

  "prov:Entity": [


        {"@id": "niiri:bids_data1", "label": "Bids dataset 1", "prov:atLocation": "data/bids_root"},


      {


              "@id": "niiri:fmri_prep_output1",


              "label": "FMRI prep output 1",


              "prov:atLocation": "out/",


              "generatedAt": "2019-10-10T10:00:00",


              "wasGeneratedBy": "niiri:fMRIPrep1"


      },

  ]


#### What if I have a group of tasks, belonging to a subgroup of tasks ?

You can the `prov-O` isPartOf relationship to add an extra link to you activity

"prov:Activity": [

    {"@id": "niiri:activity_group1", "label": "Activity Group 1", "command": "launch.sh"},

    {


          "@id": "niiri:activity_1",


          "label": "Activity 1",


          "command": "task_specific_executable.sh --arg 1",


          "parameters": {"arg1" : 1},


          "wasAssociatedWith": "RRID:SCR_007037",


          "startedAtTime": "2019-10-10T10:00:00",


          "endedAtTime": "2019-10-10T10:00:00",


          "used": "niiri:entity_1"


        }

  ],

  "prov:Entity": [

      {"@id": "niiri:entity_1", "label": "Entity 1", "prov:atLocation": "/root/file.xyz"},

  ]

  


---


## WIP -- What is under this line is being transferred above... {#wip-what-is-under-this-line-is-being-transferred-above}


## Encoding Provenance In BIDS {#encoding-provenance-in-bids}

i. Provenance information SHOULD be included in a BIDS dataset when possible.

ii. Provenance records MUST use the [PROV model](https://www.w3.org/TR/prov-o/) ontology and SHOULD be augmented by terms curated in the BIDS specification, the [NIDM](http://nidm.nidash.org/) model, and future enhancements to these models.

iii. If provenance records are included, these records of provenance of a dataset or a file MUST be described using a `[&lt;prefix>_]prov.jsonld` file. Since these [jsonld](https://json-ld.org/) documents are graph objects, they can be aggregated without the need to apply any inheritance principle. 

iv. The provenance file MAY be used to reflect the _provenance of a dataset, a collection of files or a specific file at any level _of the bids hierarchy. 

v. Provenance information SHOULD be anonymized/de-identified as necessary. 


## Possible places to encode provenance {#possible-places-to-encode-provenance}

An even simpler examples for point (i) above?

xxx*dcm → T1.nii.gz

Xxx.log  → events.tsv  

This is derived mgz (not raw bids) -- points (iv) above

In this example, with this `prov.jsonld` file we encode that the T1.mgz file was generated by version 6 of the FreeSurfer software.


```
{
"@context": "https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json",
  "@id": "http://example.org/ds00000X",
  "generatedAt": "2020-01-10T10:00:00",
  "wasGeneratedBy": {
      "@id": "https://banda.mit.edu/",
      "@type": "Project",
      "startedAt": "2016-09-01T10:00:00",
      "wasAssociatedWith": { "@id": "NIH",
                             "@type": "Organization",
                             "hadRole": "Funding"
                           }
    },
  "records": {
    "prov:Entity" : [    {
      "@id": "niiri:im2020",
            "sha512": "121231221ab4534...",
      "derivedFrom": "../sub-01/anat/..._T1.nii.gz",
      "attributedTo": "RRID:SCR_001847",
      "generatedAt": "2019-01-10T10:00:00"
    }, 
    ],
    "prov:Agent" : [ 
    {
      "label": "MyFreeSurfer",
            "version": "6.0.0",
      "@id": "RRID:SCR_001847"
    }
  ]
  "prov:Activity" : [
  {
    "@id" : "niiri:sdfjknfskjn",
    "label": "produce T1.mgz",
    "wasAssociatedWith" : "RRID:SCR_001847",
    "startedAtTime": "2021-02-02T10:10:10",
    "endAtTime" : "2021-02-02T10:10:12",
    "used" : "../sub-01/anat/..._T1.nii.gz"
  ]
}
```


**File level provenance.** This follows some of the same concepts at the dataset level, but is specifically about the current file under consideration.


```
sub-01/ 
    func/
        sub-01_task-xyz_acq-test1_run-1_bold.nii.gz
        sub-01_task-xyz_acq-test1_run-1_prov.jsonld
...
{
  "@context": "https://some/url/to/bids_context.jsonld",
  "generatedAt": "2020-01-10T10:00:00",
  "sha512": "1001231221ab4534...",
  "derivedFrom": "../../../sourcedata/sub-01/...dcm",
  "attributedTo": {"@type": "SoftwareAgent",
               "version": "1.3.0",
               "RRID": "RRID:SCR_017427"
           "label": "SPM",
        "description": "If this is a custom script, treat this as a methods section",
              }
  }
```


The NIDM extensions (nidash.org)  to the PROV model would allow one to incorporate many aspects of the neuroimaging research workflow from data to results. This includes capturing who performed data collection, what software were used, what analyses were run, and what hardware and software resources (e.g., operating system and dependencies) were used.


## BIDS JSON-LD context {#bids-json-ld-context}

For most developers and users, the context will appear in the jsonld file as:

{

    "`@context": "https://some/url/to/bids_context.jsonld",`


```
  ...
}
```


Details of the context, will encode terminology that is consistent across BIDS and may itself involve separate context files. so `"https://some/url/to/bids_context.jsonld"` could look like:

{

    "`@context": ["https://some/url/to/bids_common_context.jsonld",`


```
               "https://some/url/to/bids_derivates_context.jsonld",
               "https://some/url/to/bids_provenance_context.jsonld",
               ...
              ]
}
```


Contexts are created at the BIDS organization level, and only if necessary extended by a dataset. Thus most dataset creators will be able to reuse existing contexts. For terms, many of these are already in BIDS, with additional ones being curated by the NIDM-terms grant. Additional, terms can and should be re-used from schema.org, bioschemas, and other ontologies and vocabularies whenever possible.


<!-- Footnotes themselves at the bottom. -->
## Notes
                
TO be discussed / integrated with more context : 
 - It is RECOMMENDED to place entity (file) related provenance alongside the files where it is possible (i.e. file level provenance). 
- One option is to make use of <code>[https://w3c.github.io/json-ld-syntax/#named-graphs](https://w3c.github.io/json-ld-syntax/#named-graphs)</code>.
- Note: since these jsonld documents are graph objects, they can be aggregated using RDF tools without the need to apply the inheritance principle.

[^1]:
     https://www.w3.org/TR/json-ld11/#basic-concepts
