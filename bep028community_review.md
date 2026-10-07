# Report for BEP028 after community review
Authors: Boris Clénet, Camille Maumet, Satrajit Ghosh, Yaroslav Halchenko

In the spirit of the upcoming new BEP guidelines, this report is submitted to BIDS steering and BIDS maintainers by BEP028 leads and Boris Clénet to summarize the steps undertaken and underlying rationale following feedback received during the community review of BEP028.

BEP028 was open to community review from April 20 to May 1, 2026 (see [#2045](https://github.com/bids-standard/bids-specification/discussions/2405)). In total, the BEP received 6 comments by 5 members of the BIDS community with 15 follow-up and replies.
 
 [toc]

## 1. `Digest`

### Before community review

The `Digest` field was available for JSON objects describing `Files` and `prov:Entity` inside `prov/prov-<label>_ent.json` files. The field could also be stored inside a sidecar JSON. The field would contain checksum information for the associated data file.

Here is an example from a sidecar JSON:
```JSON
{
  "Digest": {
    "SHA-256": "66eeafb465559148e0222d4079558a8354eb09b9efabcc47cd5b8af6eed51907"
  }
}
```
where `SHA-256` is the name of the algorithm used to compute the digest `66eeaf...` from the file.

As we could not find a curated list of checksum algorithm and we wanted to allow for other algorithms than the already existing ones, we used the following description for the `Digest` field.

> Object containing digests of the file.
> Each key in the object MUST be the name of a checksum function if present in this list:
> `MD5`; `SHA1`; `SHA-224` ; `SHA-256` ; `SHA-384` ; `SHA-512` ;
> `SHA3-224`; `SHA3-256`; `SHA3-384`; `SHA3-512`; `BLAKE2B-256`; `BLAKE3-256`;
> `SHAKE128`; `SHAKE256`. Otherwise, key MAY be an arbitrary label.
> The corresponding value is the checksum as computed by the function identified by the key.

### Comments during community review

Here are the comments related to the `Digest` field.

1.A. [From @effigies](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16675519)
> The digest piece doesn't quite feel right to me:
> ```
> "Digest": {
>   "SHA-256": "66eeafb465559148e0222d4079558a8354eb09b9efabcc47cd5b8af6eed51907"
> }
> ```
> Generally, it's easier to model data when the keys are determined and the values are user-provided. I would be more comfortable with something like:
> ```
> "Checksums": [
>   {"Algorithm": "SHA-256", "Digest": "66eeafb465559148e0222d4079558a8354eb09b9efabcc47cd5b8af6eed51907"}
> ]
> ```
> I changed it to "Checksums", because "Digest" is the only thing I can think to call "66eeafb...". This is more a structural comment than a suggestion of names.

1.B. [From @robertoostenveld](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16753133)
> Why are some digest keys with and others without a dash in their name? Like MD5, SHA-224, BLAKE3-256 and SHAKE128? If this is on purpose, then that is fine with me but I would nevertheless prefer a link to an external standard that specifies the checksum identifiers.

1.C. [From @neuromechanist](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16778249)
> #### 5. Smaller items consolidating prior threads [part]
> On Digest shape and the dash-inconsistency thread: keep the object form `Digest: {<algo>: <hex>}` but lock the keys to a closed enum using IANA hash-function names (`sha-256`, `sha-512`, `blake2b-256`, `blake3-256`).

### Response

We chose [SPDX terms](https://spdx.org/rdf/terms/) for the metadata relative to digests. (SPDX was identified from discussions at OHBM 2026, in particular with Stephan Heunis).

In order to be consistent with SPDX and answering 1.A., we adopted the following structure:

```
"Checksum": [
  {
    "ChecksumAlgorithm": "spdx:checksumAlgorithm_sha256",
    "ChecksumValue": "45485541db5734f565b7cac3e009f8b02907245fc6db435c700e84d1037773b5"
  }
]
```

Where the term `Checksum` replaces `Digest`, and we store checksum objects in an array.

We updated BEP028 specification with the following description for the `ChecksumAlgorithm` field:
> URI of the algorithm used to compute the checksum.
> If the algorithm is listed as an [SPDX `spdx:ChecksumAlgorithm`](https://spdx.org/rdf/terms/#d4e2129) then the URI MUST be as provided by SPDX (for example: spdx:checksumAlgorithm_sha256, spdx:checksumAlgorithm_md5, spdx:checksumAlgorithm_blake3).

In addition, we updated the [provenance context](https://bids-specification--2099.org.readthedocs.build/en/2099/provenance-context.json) with the following new terms:

```JSON
"spdx": "http://spdx.org/rdf/terms#",
"Checksum": "spdx:Checksum",
"ChecksumAlgorithm": "spdx:ChecksumAlgorithm",
"ChecksumValue": "spdx:ChecksumValue"
```

## 2. `Command` field and the `code/` directory

### Before community review

The `Command` field for [activities](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#activities) has the following description:

> Command (or commands) performed by the activity, including all parameters.
> Set to `null` to describe that the activity was performed manually.

### Comments during community review

2.A. [From @markmikkelsen](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16675656)
> Regarding the `Command` key, the values could get quite long. Is there a better way to include such metadata? Perhaps referring to metadata in `code/`?

2.B. [From @neuromechanist](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16753133)
> #### 3. Command as a single string doesn't fit time-series pipelines
> [...] what's missing is demonstration and time-series-shaped patterns, every worked example, every example dataset, and most implicit assumptions in the prose ([...], `Command` as a one-line CLI invocation) are MRI-shaped.
> [...] +1 to the Command-length thread; the problem is broader. A 300-line EEGLAB .m file can't be a JSON string. [...]
>
> Concretely: allow Command to be string, ordered array of strings, or null; add CommandFile (relative path into code/, paired with Digest to pin the version); add Parameters (free-form object, the single most useful addition for EEG/MEG/iEEG, also lets fMRIPrep replace the config-file-digest dance); and document a canonical pattern for manual/GUI activities, Command: null, Description REQUIRED, Parameters MAY hold operator decisions like {"RejectedComponents": [3,7,12], "BadChannels": ["T7","P9"]}. [...]

### Response

We illustrated how the `Command` field can be used in different ways, based on the following examples:

The SPM example, PR [[BEP028] provenance - SPM preprocessing #497](https://github.com/bids-standard/bids-examples/pull/497) demonstrates that `Command` can contain parts of a global `.m` file corresponding to an activity.

The Nilearn example, PR [[BEP028] provenance - custom script using Nilearn #524](https://github.com/bids-standard/bids-examples/pull/524) demonstrates that `Command` can contain a command that is a call to a script file stored inside (e.g. in the `code/` directory) or outside the dataset (e.g. in a software repository). 

As a note, there used to be a `Parameter` field in a previous iteration of BIDS-Prov. This was removed to avoid duplicated information with the `Command` field. This is traced in an issue in the BEP028 repository (see [#182](https://github.com/bids-standard/BEP028_BIDSprov/issues/182)) and may be re-considered in future version of BIDS. 

No changes to the specification were made consequently to these comments.

## 3. `ent` suffix and the `prov:Entity` term

### Before community review

The specification includes references to the `prov:Entity` term from W3C PROV:

> This section specifies how to describe input and output data for [activities](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#activities).
> This data corresponds to the W3C PROV [prov:Entity](https://www.w3.org/TR/2013/REC-prov-o-20130430/#Entity) class that includes files, datasets and other types of data.
>
> Each file with a `ent` suffix is a JSON file describing input and output data.
>
> !!! note
>     The `ent` suffix stands for prov:Entity.

`prov:Entity` is also a field that can be stored in files with a `ent` suffix.

| Key name | Requirement Level | Data type | Description |
| ----------- | -------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------- |
| prov:Entity | OPTIONAL, but REQUIRED if Files and Datasets fields are absent | array of objects | Objects describing prov:Entity objects other than files or datasets. |

We wanted to have a strong consistency between the terms used by the BEP and the ones from W3C PROV while trying to avoid as much as possible the use of the term "entity", which is already a BIDS term. Therefore the specification refers to "Input and output data" (files or datasets) while still opening for other types of prov:Entity.

### Comments during community review

3.A. [From @markmikkelsen](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16685939)
> Instead of `ent` for input and output data, wouldn't something like `io` make more sense?

3.B. [From @neuromechanist](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16778249)
> #### 5. Smaller items consolidating prior threads [part]
> On prov:Entity naming: genuine clash with BIDS "entity" (the key-value building block of filenames). Either rename the suffix and array key (io/Inputs+Outputs, or Transput) or keep ent tied to W3C PROV but rename the JSON key from prov:Entity to Resources/Items with the context-file mapping back to prov:Entity. Status quo will confuse every BIDS author.
> Resolve the prov:Entity vs BIDS-entity naming clash.

### Response

The `ent` suffix was replaced by `io` to be more consistent with the specification and avoid confusion with BIDS entity. The content of these files remains unchanged and still stores objects mapping to `prov:Entity` or `prov:Collection`, as indicated in the [provenace context](https://bids-specification--2099.org.readthedocs.build/en/2099/provenance-context.json):

```JSON
"Files": "prov:Entity",
"Datasets": "prov:Collection",
```

We kept the use of `prov:Entity`, as we believe that the namespace `prov:` disambiguates the term from BIDS entity. `prov:Entity` remains a field that can be used in [files describing "Input and output data"](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#input-and-output-data).

## 4. Software resolvability

### Before community review

Software packages can be described and identified using the following fields:

| Key name | Requirement Level | Data type | Description |
| ----------- | -------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------- |
| Label | REQUIRED | string | Name of the software package. Corresponds to RDF Schema rdfs:label. |
| Version | REQUIRED | string | Version of the software package. |
| AlternativeIdentifier | OPTIONAL | array of strings | URI(s) of (an) alternative identifier(s) (such as RRID) for the software package. |

Software environments can be described and identified using the following fields:

| Key name | Requirement Level | Data type | Description |
| ----------- | -------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------- |
| Label | REQUIRED | string | Name of the environment. Corresponds to RDF Schema rdfs:label. |
| AlternativeIdentifier | OPTIONAL | array of strings | URI(s) of (an) alternative identifier(s) for the environment. |


### Comments during community review

4.A. [From @arnodelorme](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16756811)
> Is there a required way to actually resolve or locate the software? There does not seem to be a standard place to record things like a Git commit, container digest, or binary checksum, whereas other modern provenance frameworks (e.g., SLSA) explicitly capture repository location, build details, and artifact hashes.

4.B. [From @neuromechanist](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16778249)
> #### 4. Software resolvability, strengthen, don't bloat
> Echoing the resolvability thread: Version-only is unresolvable ({Label: "preproc", Version: "1.0"} means nothing), but full SLSA is overkill. A Software record SHOULD carry at least one of AlternativeIdentifier (RRID is the canonical case, RRID:SCR_007292 EEGLAB, RRID:SCR_005624 FieldTrip, RRID:SCR_005189 MNE-Python, RRID:SCR_005972 SPM); CodeURL with optional #commit; Container.Tag+Container.Digest; or a canonical package Name+Version. Version-only should be a validator WARNING, not a hard error. Add worked examples for each path plus one "no canonical identifier, custom MATLAB in code/" case.

### Response

We outlined that although software resolvability may be very useful in many instances, this is not a requirement in BIDS-Prov.

We also illustrated how, when a unique identifier is available for the software, `AlternativeIdentifier` can be used to store that identifier.

The [Provenance of DICOM to NIfTI conversion with `dcm2niix`](https://github.com/bclenet/bids-examples/tree/BEP028_dcm2niix/provenance_dcm2niix) examples shows how to use it for an RRID:

```JSON
{
  "Software": [
    {
      "Id": "bids::prov#dcm2niix-khhkm7u1",
      "Label": "dcm2niix",
      "Version": "v1.0.20220720",
      "AlternativeIdentifier": [
        "RRID:SCR_023517"
      ]
    }
  ]
}
```

Similarly for a software stored on Github, uniquely identified by a tag, the [Provenance of fMRI first-level analysis with `Nilearn`](https://github.com/bclenet/bids-examples/tree/BEP028_nilearn/provenance_nilearn) shows we can have: 

```JSON
{
  "Software": [
    {
      "Id": "bids::prov#nilearn-JAk1fM3q",
      "Label": "Nilearn",
      "Version": "0.12.0",
      "AlternativeIdentifier": [
        "https://github.com/nilearn/nilearn/releases/tag/0.12.0"
      ]
    }
  ]
}
```

No changes to the specification were made consequently to these comments.

## 5. Missing examples

### Before community review

BEP028 comes with the following examples:

 * [provenance_dcm2niix](https://github.com/bids-standard/bids-examples/tree/BEP028_omnibus/provenance_dcm2niix): Provenance metadata for a DICOM to NIfTI conversion with dcm2niix.
 * [provenance_fmriprep](https://github.com/bids-standard/bids-examples/tree/BEP028_omnibus/provenance_fmriprep): Provenance metadata for a fMRI preprocessing with fMRIPrep
 * [provenance_heudiconv](https://github.com/bids-standard/bids-examples/tree/BEP028_omnibus/provenance_heudiconv): Provenance of DICOM to NIfTI conversion with heudiconv
 * [provenance_manual](https://github.com/bids-standard/bids-examples/tree/BEP028_omnibus/provenance_manual): Provenance of manual brain segmentations
 * [provenance_nilearn](https://github.com/bids-standard/bids-examples/tree/BEP028_omnibus/provenance_nilearn): Provenance of fMRI first-level analysis with Nilearn
 * [provenance_spm](https://github.com/bids-standard/bids-examples/tree/BEP028_omnibus/provenance_spm): Provenance of fMRI preprocessing with SPM

### Comments during community review

5.A. [From @neuromechanist](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16778249)
> #### 1. All six example datasets are MRI

> [...] what's missing is demonstration and time-series-shaped patterns, every worked example, every example dataset, and most implicit assumptions in the prose (containerised pipelines, DICOM, single long activity per subject, Command as a one-line CLI invocation) are MRI-shaped. 

### Response

A new example for provenance of time-series was included and another one is in progress:
* Provenance description of the Zhou2016 dataset preprocessed with EEGPrep.
    * [Derivative dataset with provenance](https://github.com/bclenet/nm000226_test/blob/provenance) (software environment is a Python virtual environment)
    * [Derivative dataset with provenance](https://github.com/bclenet/nm000226_test/blob/provenance_docker) (software environment is a Docker container)
    * [Corresponding bids-example](https://github.com/bclenet/bids-examples/tree/BEP028_eeglab/provenance_eegprep) to be added in the BEP028 omnibus.
* (Work in progress) Provenance description of a typical fieltrip tutorial. 
    * [Issue created on the fieldtrip project](https://github.com/fieldtrip/website/issues/934)


## 6. Light-weight representation of the provenance within a single-file

### Comment during community review
6.A. [From @neuromechanist](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16778249)
> #### 2. The three-tier model is too heavy for typical time-series work
> Sidecar GeneratedBy + dataset_description.GeneratedBy + /prov/{act,soft,env,ent}.json maps cleanly to fMRIPrep/SPM. It does not map to a typical EEG/EMG study: one PI, one MATLAB script, no Docker, no DataLad, often no git; hundreds of small companion sidecars per recording; the same activity reused across many runs; manual steps with no Command. Applied literally that produces hundreds of sidecars carrying GeneratedBy, four prov-<label>_*.json per stage, and an _env.json that does nothing.

### Response
    
An example for a docker-based EEG study was provided (see 5. Missing examples) to better examplify how the BEP can apply to EEG data. Another example is in-progress for an EEG analysis based on FieldTrip using a single MATLAB script. In principle this will be very similar to the [SPM processing example](https://github.com/bids-standard/bids-examples/tree/BEP028_omnibus/provenance_spm).

## 7. Provenance of BIDS tsv files
    
### Before community review

There are several locations to store provenance metadata of files inside a dataset, a stated in the specification:

[Provenance of a BIDS file](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#provenance-of-a-bids-file)
> Provenance of a BIDS data file SHOULD be stored inside its sidecar JSON.

[Provenance files](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#provenance-files)
> Any provenance information that can't be stored in either sidecar JSON files (see Provenance of BIDS file) or in dataset_description.json (see Provenance of BIDS dataset) MUST be stored in provenance files under the /prov/ directory.

### Comment during community review

7.A. [From @neuromechanist](https://github.com/bids-standard/bids-specification/discussions/2405#discussioncomment-16778249)
> #### 6. Events / stimuli / HED, the missing modality
> For time-series datasets, provenance for events.tsv and stimuli is more important than provenance for the raw recording: the same EEG file reanalyzed with three event-extraction passes and three HED annotations gives three different scientific results. The spec doesn't mention events.tsv, HED, or BEP044 (PR #2022). Please add normative coverage and one worked example: _events.json with GeneratedBy for HED annotation of a stimulus log; stim-<label>.json (BEP044) with GeneratedBy for stimulus rendering; stim-<label>_annot-<label>_events.tsv with GeneratedBy for the time-varying annotation. The first is independently useful even if BEP044 lands later, coordinating now avoids re-litigating events provenance in another BEP.
    
### Response
Provenance of TSV files can be stored using the same approach as for other BIDS files (e.g. images), either in its sidecar JSON (when available) see [Provenance of a BIDS file](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#provenance-of-a-bids-file) or (when there is no sidecar JSON) using the `prov` folder see [Provenance files](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#provenance-files). 
    
To clarify this, we removed "data" in "BIDS data file" in the description of "Provenance of a BIDS file", see updated specification: [Provenance of a BIDS file](https://bids-specification--2099.org.readthedocs.build/en/2099/modality-agnostic-files/provenance.html#provenance-of-a-bids-file).