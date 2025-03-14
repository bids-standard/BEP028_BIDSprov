# BIDS Extension Proposal 28 (BEP028) - Provenance: BIDS-Prov

*version 0.0.1 (draft) - Available under the CC-BY 4.0 International license.*

**Extension moderators/leads:** Satra Ghosh &lt;[satra@mit.edu](mailto:satra@mit.edu)> and Camille Maumet &lt;[camille.maumet@inria.fr](mailto:camille.maumet@inria.fr)>

**Contributors:** Stefan Appelhoff, Chris Markiewicz, Yaroslav O. Halchenko, Cyril R. Pernet, Jean-Baptiste Poline, Rémi Adon, Michael Dayan, Sarah Saneei, Eric Earl, Tibor Auer, Ghislain Vaillant, Matthieu Joulot, Omar El Rifai, Ryan J. Cali, Thomas Betton, Cyril Regan, Hermann Courteille, Arnaud Delorme, Boris Clénet.

We meet every two weeks by videoconference on Mondays at 7-8am PDT / 10am-11am EDT / 3-4pm BST. The group is always open to new contributors interested in neuroimaging data sharing. To join the call or to ask any question, please email us at [incf-nidash-nidm@googlegroups.com](mailto:incf-nidash-nidm@googlegroups.com).

---

This document contains a draft of the Brain Imaging Data Structure standard extension. It is a community effort to define standards in data / metadata. This is a working document in draft stage and any comments are welcome. 

This specification is an extension of BIDS, and general principles are shared. The specification should work for many different settings and facilitate the integration with other imaging methods.

To see the original BIDS specification, see [this link](https://bids-specification.readthedocs.io/). This document inherits all components of the original specification (e.g. how to store imaging data, events, stimuli and behavioral data), and should be seen as an extension of it, not a replacement.

---

## Table of contents

[[TOC]]

## 1. Overview

### 1.1 Goals

Interpreting and comparing scientific results and enabling reusable data and analysis output require understanding provenance, i.e. how the data were generated and processed. To be useful, the provenance must be comprehensive, understandable, easily communicated, and captured automatically in machine accessible form. Provenance records are thus used to encode transformations between digital objects.

This specification is aimed at describing the provenance of a BIDS dataset. This description is retrospective, i.e. it describes a set of steps that were executed in order to obtain the dataset (this is different from prospective descriptions of workflows that could for instance list all sets of steps that can be run on this dataset).

### 1.2 Which type of provenance is covered in this BEP?

Provenance comes up in many different contexts in BIDS. This specification focuses on representing the processings that were applied to a dataset. These could be for instance:

1. The raw conversion from DICOM images or other instrument native formats to BIDS layout, details of stimulus presentation and cognitive paradigms, and clinical and neuropsychiatric assessments, each come with their own details of provenance.
2. In BIDS derivatives, the consideration of outputs requires knowledge of which inputs from the BIDS dataset were used together with what software was run in what environment and with what parameters.

> [!CAUTION]
> TODO: those above should be covered with their own example

But provenance comes up in other contexts as well, which might be addressed at a later stage:

3. For datasets and derivatives, provenance can also include details of why the data were collected in the first place covering hypotheses, claims, and prior publications. Provenance can encode support for which claims were supported by future analyses.
4. Provenance can involve information about people and institutions involved in a study.
5. Provenance records can highlight reuse of datasets while providing appropriate attribution to the original dataset generators as well as future transformers.  

Provenance can be captured using different mechanisms, but independent of encoding, always reflects transformations by either humans or software. The interpretability of provenance records requires a consistent vocabulary for provenance as well as an expectation for a consistent terminology for the objects being encoded. 

> [!NOTE]
> Some level of provenance is already encoded in BIDS : the [`GeneratedBy`](https://bids-specification.readthedocs.io/en/stable/glossary.html#generatedby-metadata) field of the `dataset_description.json` file can contain the provenance metadata for a dataset. This BEP avoids duplicating information already available in JSON files.

## 1.3 Principles for encoding provenance In BIDS

1. Provenance information SHOULD be included in a BIDS dataset when possible.
2. If provenance records are included, these MUST be described using the conventions detailed by the BIDS-Prov specification.
3. BIDS-Prov MAY be used to reflect the provenance of a dataset, a collection of files or a specific file at any level of the bids hierarchy. 
4. Provenance information SHOULD be anonymized/de-identified as necessary. 

### 1.4 Provenance format

BIDS-Prov metadata is written in JSON or JSON-LD. JSON-LD is a specific type of JSON that allows encoding graph-like structures with the Resource Description Framework.[^1]

BIDS-Prov records use the PROV model ontology [^2], augmented by terms curated in this specification, and defined in the [BIDS-Prov context](/context.json).

A skeleton for a BIDS-Prov JSON-LD file looks like this:
```
{
    "@context": "https://purl.org/nidash/bidsprov/context.json",  
    "BIDSProvVersion": "0.0.1",
    "Records": {
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
            },
            {
                    <...Activity 2...>
            }
        ],
        "Entity": [
            {
                    <...Entity 1...>
            },
            {
                    <...Entity 2...>
            }
        ],
        "Environment": [
            {
                    <...Environment 1...>
            },
            {
                    <...Environment 2...>
            }
        ]
  }
}
```

<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>@context</code>
   </td>
   <td>REQUIRED. A URL to the BIDS-Prov json context. Value must be <code>"https://purl.org/nidash/bidsprov/context.json"</code>
   </td>
  </tr>
  <tr>
   <td><code>BIDSProvVersion</code>
   </td>
   <td>REQUIRED. A string identifying the version of the specification adhered to.
   </td>
  </tr>
  <tr>
   <td><code>Records</code>
   </td>
   <td>REQUIRED. A list of provenance records (Activity, Entity, Agent, Environment), describing the provenance (see the <a href="#2-provenance-records">2. Provenance records</a> section below).
   </td>
  </tr>
</table>

BIDS-Prov allows this skeleton to be split into several *JSON* files. This is described in sections [3.1.3 Suffixes](#3-1-3-suffixes)
and [3.2 Provenance description levels](#3-2-provenance-description-levels).

Using tools provided by BIDS-Prov ([5. Tools](#5-tools)), these JSON contents can be merged back to a structured JSON-LD as described above.

> [!NOTE]
> Since the JSON-LD documents are graph objects, they can be aggregated using RDF tools without the need to apply the inheritance principle.

> [!WARNING]
> A group of provenance records MUST be described:
> * either in several `.json` files ;
> * or in one `.jsonld` file.

A complete schema for the model file to facilitate specification and validation is available from [https://github.com/bids-standard/BEP028_BIDSprov](https://github.com/bids-standard/BEP028_BIDSprov). In the event of disagreements between the schema and the specification, the specification is authoritative.

## 2. Provenance records

BIDS-Prov metadata consists in a set or records. There are 4 types of records: `Activity`, `Entity`, `Agent`, and `Environment`.

Activities represent the transformations that have been applied to the data. Each Activity can use Entities as inputs and outputs. The Agent specifies the software package. Environments specify the software environment in which the provenance record was obtained.

![](img/records.svg)

### 2.1 Activity
Each Activity record is a JSON Object with the following fields:

> [!CAUTION]
> TODO: AssociatedWith and Used can also entirely describe the Agent (resp. Entity)
> TODO: AssociatedWith and Used can be lists
> TODO: Can an Activity represent a group of command lines ? If so, Command can be a list

<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>Id</code>
   </td>
   <td>REQUIRED. Unique URIs (for example a UUID). Identifier for the  activity.
   </td>
  </tr>
  <tr>
   <td><code>Label</code>
   </td>
   <td>REQUIRED. String. Name of the tool, script, or function used (e.g. “bet”, "recon-all", "myFunc", "docker").
   </td>
  </tr>
  <tr>
   <td><code>Command</code>
   </td>
   <td>REQUIRED. String. Command used to run the tool, including all parameters.
   </td>
  </tr>
  <tr>
   <td><code>AssociatedWith</code>
   </td>
   <td>OPTIONAL. UUID. Identifier of the software package used to compute this activity (the corresponding Agent must be defined with its own Agent record).
   </td>
  </tr>
  <tr>
   <td><code>Used</code>
   </td>
   <td>OPTIONAL. List. Identifiers (UUIDs) of entities or environments used by this activity. The corresponding Entities (resp. Environments) must be defined with their own Entity (resp. Environment) record).
   </td>
  </tr>
  <tr>
   <td><code>Type</code>
   </td>
   <td>OPTIONAL. URI. A term from a controlled vocabulary that more specifically describes the Activity.
   </td>
  </tr>
  <tr>
   <td><code>StartedAtTime</code>
   </td>
   <td>OPTIONAL. xsd:<em>dateTime. </em>A timestamp tracking when this activity started
   </td>
  </tr>
  <tr>
   <td><code>EndedAtTime</code>
   </td>
   <td>OPTIONAL. xsd:<em>dateTime. </em>A timestamp tracking when this activity ended
   </td>
  </tr>
</table>

Here is an example of an Activity record:
```JSON
{
    "Id": "bids::prov/#conversion-00f3a18f",
    "Label": "Dicom to Nifti conversion",
    "Command": "dcm2niix -o . -f sub-%i/anat/sub-%i_T1w sourcedata/dicoms",
    "AssociatedWith": "bids::prov/#dcm2niix-khhkm7u1",
    "Used": [
        "bids::prov/#fedora-uldfv058",
        "bids::sourcedata/dicoms"
    ],
    "Type": "Activity",
    "StartedAtTime": "2025-03-13T10:26:00",
    "EndedAtTime": "2025-03-13T10:26:05"
}
```

### 2.2 Entity
Each Entity record is a JSON Object with the following fields:

> [!CAUTION]
> TODO: GeneratedBy can also entirely describe the Activity
> TODO: GeneratedBy can be a list

<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>Id</code>
   </td>
   <td>REQUIRED. Unique URIs (for example a UUID). Identifier for the entity.
   </td>
  </tr>
  <tr>
   <td><code>Label</code>
   </td>
   <td>REQUIRED. String. A name for the entity.
   </td>
  </tr>
  <tr>
   <td><code>AtLocation</code>
   </td>
   <td>OPTIONAL. String. For input files, this is the relative path to the file on disk.
   </td>
  </tr>
  <tr>
   <td><code>GeneratedBy</code>
   </td>
   <td>OPTIONAL. UUID. Identifier of the activity which generated this entity (the corresponding Activity must be defined with its own Activity record).
   </td>
  </tr>
  <tr>
   <td><code>Type</code>
   </td>
   <td>OPTIONAL. URI. A term from a controlled vocabulary that more specifically describes the Entity.
   </td>
  </tr>
  <tr>
   <td><code>Digest</code>
   </td>
   <td>RECOMMENDED. Dict. For files, this would include checksums of files. It would take the form {"<checksum-name>": "value"}.
   </td>
  </tr>
</table>

Here is an example of an Entity record:
```JSON
{
    "Id": "bids::sub-02/anat/sub-02_T1w.nii",
    "Label": "sub-02_T1w.nii",
    "AtLocation": "sub-02/anat/sub-02_T1w.nii",
    "GeneratedBy": "bids::prov/#conversion-00f3a18f",
    "Type": "Activity",
    "Digest": {
        "SHA-256": "42d8faeaa6d4988a9233a95860ef3f481fb0daccce4c81bc2c1634ea8cf89e52"
    }
}
```

### 2.3 Agent (Optional)
Agent records are OPTIONAL. If included, each Agent record is a JSON Object with the following fields:

> [!CAUTION]
> TODO: do we need a Type field for Agent?
> TODO: shall we use `Software`, `Agent`, `SoftwareAgent` ?

<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>Id</code>
   </td>
   <td>REQUIRED. A unique identifier like a UUID that will be used to associate activities with this software (e.g., urn:1264-1233-11231-12312, "urn:bet-o1ef4rt"
   </td>
  </tr>
  <tr>
   <td><code>AltIdentifier</code>
   </td>
   <td>OPTIONAL. URI. URI of the RRID for this software package (cf. <a href="https://scicrunch.org/resources/about/Getting%20Started">scicrunch</a>).
   </td>
  </tr>
  <tr>
   <td><code>Label</code>
   </td>
   <td>REQUIRED. String. Name of the software.
   </td>
  </tr>
  <tr>
   <td><code>Version</code>
   </td>
   <td>REQUIRED. String. Version of the software.
   </td>
  </tr>
</table>

Here is an example of an Agent record:
```JSON
{
    "Id": "bids::prov/#dcm2niix-khhkm7u1",
    "AltIdentifier": "RRID:SCR_023517",
    "Label": "dcm2niix",
    "Version": "v1.0.20220720"
}
```

### 2.4 Environment (Optional)
Environment records are OPTIONAL. If included, each Environment record is a JSON Object with the following fields:

> [!CAUTION]
> TODO: do we need a Type field for Environment?
> TODO: Environment not currently defined in the BIDS-Prov context

<table>
  <tr>
   <td><strong>Key name</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><code>Id</code>
   </td>
   <td>REQUIRED. Unique URIs (for example a UUID). Identifier for the environment (this identifier will be used to associated activities with this environment).
   </td>
  </tr>
  <tr>
   <td><code>Label</code>
   </td>
   <td>REQUIRED. String. Name of the software.
   </td>
  </tr>
  <tr>
   <td><code>EnvVars</code>
   </td>
   <td>OPTIONAL. Dict. A dictionary defining the environment variables as key-value pairs. 
   </td>
  </tr>
  <tr>
   <td><code>OperatingSystem</code>
   </td>
   <td>OPTIONAL. String. Name of the operating system.
   </td>
  </tr>
  <tr>
   <td><code>Dependencies</code>
   </td>
   <td>OPTIONAL. Dict. A dictionary defining the software used and their versions as key-value pairs.
   </td>
  </tr>
</table>

Here is an example of an Environment record:
```JSON
{
    "Id": "bids::prov/#fedora-uldfv058",
    "Label": "Fedora release 36 (Thirty Six)",
    "OperatingSystem": "GNU/Linux 6.2.15-100.fc36.x86_64"
}
```

## 3. Additions to BIDS

### 3.1 File naming

This section describes additions to the BIDS naming conventions for BIDS-Prov files.

For further information about naming conventions, please consult the BIDS specification ([https://bids-specification.readthedocs.io](https://bids-specification.readthedocs.io)). Until these conventions are established in BIDS, it is RECOMMENDED to use the following.

#### 3.1.1 File extensions

BIDS-Prov files contain JSON or JSON-LD data, hence having either a `.json` or a `.jsonld` extension.

When using a `.jsonld` extension, the contents of the file must be JSON-LD.

As JSON-LD is JSON, `*.jsonld` files can contain JSON.

#### 3.1.2 The `prov` entity

BIDS-Prov introduces the following entity:

`prov`
* Full name: Provenance records
* Format: `prov-<label>`
* Definition: A grouping of provenance records. Defining multiple provenance records groups is appropriate when several processings have been performed on data.

In the following example, two separated processings (`conversion` and `smoothing`) were performed on the data, resulting in two groups of provenance records.
```
└─ dataset
   ├─ sub-001/
   │  └─ prov/
   │     └─ sub-001_prov-smoothing_act.json
   └─ prov/
      ├─ prov-conversion_all.jsonld
      ├─ prov-smoothing_base.json
      ├─ prov-smoothing_soft.json
      ├─ prov-smoothing_ent.json
      └─ ... 
```

#### 3.1.3 Suffixes

The following BIDS suffixes specify the contents of a provenance file.

<table>
  <tr>
   <td><strong>Suffix</strong>
   </td>
   <td><strong>File contents</strong>
   </td>
   <td><strong>File extension</strong>
   </td>
  </tr>
  <tr>
   <td><code>act</code>
   </td>
   <td>Activity records for the group of provenance
   </td>
   <td><code>.json</code>
   </td>
  </tr>
  <tr>
   <td><code>ent</code>
   </td>
   <td>Agent records for the group of provenance
   </td>
   <td><code>.json</code>
   </td>
  </tr>
  <tr>
   <td><code>env</code>
   </td>
   <td>Entity records for the group of provenance
   </td>
   <td><code>.json</code>
   </td>
  </tr>
  <tr>
   <td><code>base</code>
   </td>
   <td>Common parameters for the group of provenance (<code>BIDSProvVersion</code> and <code>@context</code>).
   <td><code>.json</code>
   </td>
   </td>
  </tr>
  <tr>
   <td><code>all</code>
   </td>
   <td>All records for the group of provenance records.
   </td>
   <td><code>.jsonld</code>
   </td>
  </tr>
</table>

### 3.2 Provenance description levels

This section describes the places where BIDS-Prov metadata can be stored.

For further information about organization conventions, please consult the BIDS specification ([https://bids-specification.readthedocs.io](https://bids-specification.readthedocs.io)). Until these conventions are established in BIDS, it is RECOMMENDED to use the following.

BIDS-Prov metadata can be stored at different levels:
* at dataset level ;
* inside dataset subdirectories ;
* at file level.

It is recommended that the records are stored at the level they describe. E.g.:
* an Activity that generated as set of files for several subjects of the dataset must be described at the dataset level ;
* an Activity that generated as set of files for one subject only must be described at the subject's subdirectory level ;
* an Activity that generated one file only can be described at this file's level.

#### 3.2.1 File level provenance

BIDS-Prov provenance metadata can be stored inside the sidecar JSON of any BIDS file (or BIDS-Derivatives file) it applies to.
In this case, the BIDS-Prov content only refers to the associated data file.

The sidecar JSON naming convention is already defined by BIDS. Here is an example dataset tree:
```
└─ example_dataset
   ├─ sub-001/
   │  └─ ses-01/
   │     └─ anat/
   │        ├─ sub-001_ses-01_T1w.nii.gz
   │        └─ sub-001_ses-01_T1w.json
   ├─ sub-002/
   │  └─ ses-01/
   │     └─ anat/
   │        ├─ sub-002_ses-01_T1w.nii.gz
   │        └─ sub-002_ses-01_T1w.json
   ├─ ...
   └─ dataset_description.json
```

Inside the sidecar JSON, the `GenearatedBy` field must describe the `Activity` that generated the data file, either with a reference to an existing `Id`:

```JSON
{
    "GeneratedBy": "urn:conversion-00f3a18f",
}
```

or with a complete description of the `Activity` if it was not described elsewhere.

```JSON
{
    "GeneratedBy": {
        "Id": "urn:conversion-00f3a18f",
        "Label": "Conversion",
        "Command": "convert -i raw_file.ext -o sub-001_ses-01_T1w.nii.gz"
    }
}
```

Based on the same principle, the `SidecarGenearatedBy` field can be defined to describe the `Activity` that generated the sidecar JSON file.
If the `SidecarGenearatedBy` field is not defined, BIDS-Prov assumes that the sidecar JSON was generated by the `Activity` described in the `GenearatedBy` field.

No other field is allowed to describe provenance inside sidecar JSONs.

> [!CAUTION]
> TODO: where are the @context and BIDSProvVersion ?

#### 3.2.2 Subdirectories level provenance

BIDS-Prov files can be stored in a `prov/` directory in any subdirectory of the dataset (or BIDS-Derivatives directories).

In this case, the provenance metadata applies to the data files inside or below in the directory tree ; as stated by [BIDS common principles](https://bids-specification.readthedocs.io/en/stable/common-principles.html#filesystem-structure).

Each BIDS-Prov file must meet the following naming convention. The `label` of the `prov` entity is arbitrary, `suffix` is one of listed in [3.3.1 Suffixes](#3-1-3-suffixes), and `extension` is either `json` or `jsonld`.

```
sub-<label>/
  [ses-<label>/]
    prov/
      sub-<label>[_ses-<label>]_prov-<label>_<suffix>.<extension>
```

Here is an example dataset tree:

```
└─ dataset
   ├─ sub-001/
   │  ├─ prov/
   │  │  └─ sub-001_prov-dcm2niix_act.json
   │  └─ ses-01/
   │     ├─ prov/
   │     │  └─ sub-001_ses-01_prov-dcm2niix_act.json
   │     └─ ...
   ├─ sub-002/
   │  ├─ prov/
   │  │  └─ sub-002_prov-dcm2niix_act.json
   │  └─ ...
   ├─ ...
   └─ dataset_description.json
```

> [!CAUTION]
> TODO: where are the @context and BIDSProvVersion ?

#### 3.2.3 Dataset level provenance - `prov/` directory

BIDS-Prov files can be stored in a `prov/` directory immediately below the BIDS dataset (or BIDS-Derivatives dataset) root. At the dataset level, provenance can be about any BIDS file in the dataset.

Each BIDS-Prov file must meet the following naming convention. The `label` of the `prov` entity is arbitrary, `suffix` is one of listed in [3.1.3 Suffixes](#3-1-3-suffixes), and `extension` is either `json` or `jsonld`

```
prov/
  [<subdirectories>/]
    prov-<label>_<suffix>.<extension>
```

Here is an example:

```
└─ dataset
   ├─ prov/
   │  ├─ dcm2niix/
   │  │  └─ prov-dcm2niix_base.jsonld
   │  ├─ prov-preprocessing_base.json
   │  ├─ prov-preprocessing_soft.json
   │  └─ ... 
   ├─ sub-001/
   ├─ sub-002/
   ├─ sub-003/
   ├─ ...
   └─ dataset_description.json
```

#### 3.2.4 Dataset level provenance - `dataset_description.json` file

In the current version of the BIDS specification (1.10.0), the [`GeneratedBy`](https://bids-specification.readthedocs.io/en/stable/glossary.html#generatedby-metadata) field of the `dataset_description.json` files allows to specify provenance of the dataset.

BEP028 proposes that the following description replaces the `GeneratedBy` field as part of a major revision of the BIDS specification. Until this happens, BIDS-Prov provenance records can be stored in a `GeneratedByProv` field.

Here is an example of a `GeneratedByProv` field containing a complete description of an `Activity`:

```JSON
{
    "GeneratedByProv": {
        "Id": "bids::#conversion-00f3a18f",
        "Label": "Dicom to Nifti conversion",
        "Command": "dcm2niix -o . -f sub-%i/anat/sub-%i_T1w sourcedata/dicoms",
        "AssociatedWith": {
            "Id": "bids::#dcm2niix-khhkm7u1",
            "AltIdentifier": "RRID:SCR_023517",
            "Label": "dcm2niix",
            "Version": "v1.0.20220720",
            "Used": {
                "Id": "bids::#fedora-uldfv058",
                "Label": "Fedora release 36 (Thirty Six)",
                "OperatingSystem": "GNU/Linux 6.2.15-100.fc36.x86_64"
            }
        }
    }
}
```

Here is an example of a `GeneratedByProv` field containing the IRI of an `Entity` described in another BIDS-Prov file:

```JSON
{
    "GeneratedByProv": "bids::#conversion-00f3a18f"
}
```
> [!CAUTION]
> TODO: where are the @context and BIDSProvVersion ?

### 3.3 Consistency of IRIs

BIDS-Prov recommends the following conventions in order to have consistent, human readable, and explicit IRIs[^3] as `Id` for provenance records objects. These principles also allow to identify where a record is described.

IRIs identifying `Activity`, `Agent`, and `Environment` provenance records inside files stored in a directory `<directory>` relatively to a BIDS dataset `<dataset>` SHOULD have the following form, where `<label>` is a human readable label for the record and `<uid>` is a unique group of chars:

```
bids:<dataset>:<directory>#<name>-<uid>
```

Here are a few naming examples:
* `bids:ds001734:prov#conversion-xfMMbHK1`: an `Activity` described at dataset level inside the `ds001734` dataset;
* `bids::sub-001/prov#dcm2niix-70ug8pl5"`: an `Agent` described at subject level inside the current dataset ;
* `bids::prov#fedora-uldfv058"`: an `Environment` described at dataset level inside the current dataset.

IRI identifying `Entity` provenance records for a file `<file>` relatively to a BIDS dataset `<dataset>` SHOULD have the following form:

```
bids:<dataset>:<file>
```

derivatives/fmriprep/sub-001/func/sub-001_task-MGT_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz

Here are a few naming examples:
* `bids:ds001734:sub-002/anat/sub-02_T1w.nii`: an `Entity` describing a T1w file for subject `sub-002` in the `ds001734` dataset ;
* `bids:derivatives:fmriprep/sub-001/func/sub-001_task-MGT_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz`: an `Entity` describing a bold file for subject `sub-001` in the `derivatives` dataset.

Here is another example that considers the following dataset:

```
└─ dataset/
   ├─ sourcedata/
   │  └─ dicoms/
   │     └─ ...
   ├─ sub-001/
   │  ├─ anat/
   │  │  └─ sub-001_T1W.nii.gz
   │  └─ prov/
   │     └─ sub-001_prov-dcm2niix_act.json
   ├─ ...
   └─ prov/
      ├─ prov-dcm2niix_base.json
      └─ prov-dcm2niix_soft.json
```

IRIs of provenance records defined in `prov/prov-dcm2niix_soft.json` should start with `bids:dataset:prov#` or `bids::prov#`.
```JSON
{
    "bids:dataset:prov#dcm2niix-70ug8pl5": {
        "Label": "dcm2niix",
        "Version": "v1.1.3"
    }
}
```

This `Agent` can be referred to in the `sub-001/prov/sub-001_prov-dcm2niix_act.json` file:
```JSON
{
    "bids:dataset:sub-001/prov#conversion-00f3a18f": {
        "Label": "Conversion",
        "Command": "dcm2niix -o . -f sub-%i/anat/sub-%i_T1w sourcedata/dicoms",
        "AssociatedWith": "bids:dataset:prov#dcm2niix-70ug8pl5"
    }
}
```

## 4. Examples

A list of examples for BIDS-Prov are available in https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples

> [!CAUTION]
> TODO: some examples are not merged yet.

<table>
  <tr>
   <td><strong>Location</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>

  <tr>
   <td><a href="https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples/simple_example/">simple_example/</a>
   </td>
   <td>A simple example describing the downsampling of EEG data using EEGLAB.
   </td>
  </tr>

  <tr>
   <td><a href="https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples/from_parsers/afni/">from_parsers/afni/</a>
   </td>
   <td>A set of examples for fMRI processing using AFNI. These where generated generated from ...
   </td>
  </tr>

  <tr>
   <td><a href="https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples/from_parsers/fsl/">from_parsers/fsl/</a>
   </td>
   <td>A set of examples for fMRI processing using FSL. These where generated generated from ...
   </td>
  </tr>

  <tr>
   <td><a href="https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples/from_parsers/spm/">from_parsers/spm/</a>
   </td>
   <td>A set of examples for fMRI processing using SPM. These where generated generated from ...
   </td>
  </tr>

  <tr>
   <td><a href="https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples/dcm2niix/">dcm2niix/</a>
   </td>
   <td>A set of examples describing dicom to nifti conversion using dcm2niix. These aim at showing different ways to organise the exact same provenance records inside a dataset.
   </td>
  </tr>

  <tr>
   <td><a href="https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples/heudiconv/">heudiconv/</a>
   </td>
   <td>An example describing dicom to nifti conversion using heudiconv.
   </td>
  </tr>

  <tr>
   <td><a href="https://github.com/bids-standard/BEP028_BIDSprov/tree/master/examples/nipype/">nipype/</a>
   </td>
   <td>An example describing simple processings on anatomical MRI using FSL through Nipype.
   </td>
  </tr>

</table>

## 5. Tools

## 6. Future perspectives

Beyond what is covered in the current specification, provenance comes up in other contexts as well, which might be addressed at a later stage:
1. For datasets and derivatives, provenance can also include details of why the data were collected in the first place covering hypotheses, claims, and prior publications. Provenance can encode support for which claims were supported by future analyses.
2. Provenance can involve information about people and institutions involved in a study.
3. Provenance records can highlight reuse of datasets while providing appropriate attribution to the original dataset generators as well as future transformers.  
4. Details of stimulus presentation and cognitive paradigms, and clinical and neuropsychiatric assessments, each come with their own details of provenance.
5. Transformations made by humans (e.g., editing freesurfer, adding quality evaluations).
6. The interpretability of provenance records requires a consistent vocabulary for provenance as well as an expectation for a consistent terminology for the objects being encoded. While the current specification focuses on the former, the latter (i.e. consistent terminology for the objects being encoded) will require additional efforts.

## 7. Positioning with respect to other BIDS models

### 7.1 Provenance in BIDS derivatives

Comments/things to discuss/incorporate: 

* Yarik: we should position BIDS-Prov w.r.t. Other provenance info available in BIDS derivatives
* JB: Question on how to organize info in BIDS-Prov versus what will be available in bids-derivative sidecars

### 7.2 Justification for Separating Provenance from JSON files

Provenance is information about a file, including any metadata that is relevant to the file itself. Thus any BIDS data file and its associated JSON sidecar metadata together constitute a unique entity. As such, one may want to record the provenance of the JSON file as much as the provenance of the BIDS file. In addition, separating the provenance as a separate file for now, allows this to be an OPTIONAL component, and by encoding provenance as a JSON-LD document allows capturing the provenance as an individual record or multiple records distributed throughout the dataset.

## 8. How to encode your workflow with BIDS-prov

Either you are a software developer, a researcher striving for reproducible science, or anyone working in the neuroimaging field and willing to use BIDS-prov, at some point you might be asking yourself the following question : What is the right way to represent my workflow in the philosophy of BIDS-prov ?

### This set of examples will give you an overview of the typical cases and how to apply BIDS-prov concepts !

#### I have many activities/entities to track, should I put everything in a single file ?

Simple answer : NO. BIDS-prov has been designed for provenance records to be shared across multiple files

If you have Activity 1 and Entity 1 defined in a provenance file called init.json, this file can look like the following

```JSON
"Activity": [
    {
        "Id": "niiri:init",
        "Label": "Do some init",
        "Command": "python -m my_module.init --weights '[0, 1]'",
        "Parameters": {
            "weights" : [0, 1]
        },
        "StartedAtTime": "2020-10-10T10:00:00",
        "Used": "niiri:bids_data1"
    }
],

"Entity": [
    {
        "Id": "niiri:bids_data1",
        "Label": "Bids dataset 1",
        "AtLocation": "data/bids_root"
    }
]
```

Now if we want `Entity 2` defined in `preproc.json` to also have a "wasGeneratedBy" field referencing "Activity 1" from `init.json`, we can simply write the following

```JSON
"Entity": [
     {
        "Id": "niiri:bids_data1",
        "Label": "Bids dataset 1",
        "GeneratedBy": "niiri:init"
    }
]
```

Needless to say, both `init.json` and `preproc.json` must have the reference the same context file (in a `"@context"` field at the very top)

#### I want to track provenance for subject-level analysis, should I declare a prov file per subject ?

You can create a single prov file for every subject. Yet another option is to use globbing to group multiple files into the same entity, using globbing in the `generatedAt` field of this entity.

Files for different subjects usually share common prefixes and extensions.

```JSON
"Entity": [
    {
        "Id": "niiri:hfdhbfd",
        "Label": "anat raw files",
        "AtLocation": "sub-*/anat/sub-*_T1w.nii.gz"
    },
    {
        "Id": "niiri:fdhbfd",
        "Label": "func raw files",
        "AtLocation": "sub-*/func/sub-*_task-tonecounting_bold.nii.gz"
    }
]
```

#### One of my steps makes use of a docker container, of what type should it be ? What relations to represent ?

An example of this can be [fMRIPrep](https://fmriprep.org/en/stable/index.html), which can be launched as a docker container.

The most simplistic way you can think of is to have this container "black-boxed" in your workflow. You basically record the calling of this container (`Command` section) and the output (see the outputs section from fMRIPrep)

```JSON
"Activity": [
    {
        "Id": "niiri:fMRIPrep1",
        "Label": "fMRIPrep step",
        "Command": "fmriprep data/bids_root/ out/ participant -w work/",
        "Parameters": {
                "bids_dir" : "data/bids_root",
                "output_dir" : "out/",
                "anaysis_level" : "participant"
        },
        "Used": "niiri:bids_data1"
    }
],
"Entity": [
    {
        "Id": "niiri:bids_data1",
        "Label": "Bids dataset 1",
        "AtLocation": "data/bids_root"
    },
    {
        "Id": "niiri:fmri_prep_output1",
        "Label": "FMRI prep output 1",
        "AtLocation": "out/",
        "GeneratedAt": "2019-10-10T10:00:00",
        "GeneratedBy": "niiri:fMRIPrep1"
    }
]
```

#### What if I have a group of tasks, belonging to a subgroup of tasks ?

You can use the PROV-O `isPartOf` relationship to add an extra link to you activity

```JSON
"prov:Activity": [
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
],

"prov:Entity": [
    {
        "@id": "niiri:entity_1",
        "label": "Entity 1",
        "prov:atLocation": "/root/file.xyz"
    }
]
```

---

## WIP -- What is under this line is being transferred above... {#wip-what-is-under-this-line-is-being-transferred-above}


## BIDS JSON-LD context {#bids-json-ld-context}

For most developers and users, the context will appear in the jsonld file as:

```
{
    "@context": "https://some/url/to/bids_context.jsonld",
}
```

Details of the context, will encode terminology that is consistent across BIDS and may itself involve separate context files. so `"https://some/url/to/bids_context.jsonld"` could look like:

```
{
    "@context": [
        "https://some/url/to/bids_common_context.jsonld",
        "https://some/url/to/bids_derivates_context.jsonld",
        "https://some/url/to/bids_provenance_context.jsonld"
    ]
}
```

Contexts are created at the BIDS organization level, and only if necessary extended by a dataset. Thus most dataset creators will be able to reuse existing contexts. For terms, many of these are already in BIDS, with additional ones being curated by the NIDM-terms grant. Additional, terms can and should be reused from schema.org, bioschemas, and other ontologies and vocabularies whenever possible.

<!-- Footnotes themselves at the bottom. -->
## Notes

[^1]: https://www.w3.org/TR/json-ld11/#basic-concepts
[^2]: http://www.w3.org/TR/prov-o/
[^3]: https://www.w3.org/TR/json-ld11/#iris