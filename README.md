# BEP028
provenance framework for BIDS
This repository contains **BIDS Extension Proposal 028 : BIDS-prov, a provenance framework for BIDS**

## Our goal
**Interpreting and comparing scientific results** and enabling reusable data and analysis output require understanding provenance, i.e. how the data were generated and processed. To be useful, the provenance must be understandable, easily communicated, and captured automatically in machine accessible form. Provenance records are thus used to encode transformations between digital objects

## Who is building BEP 028
Camille Maumet ([@cmaumet](https://github.com/cmaumet)) and Rémi Adon ([@remiadon](https://github.com/remiadon)) are currently working on the definition of this BEP, as well as providing meaningful examples

Satrajit Ghosh ([@satra](https://github.com/satra)) is responsible for integration in BIDS


## How to help
[Our goal](#our-goal) is to extends BIDS to be able to track provenance at every stage of an experiment.

For this purpose we have to **propose changes to the BIDS specification**


The BIDS specification is *rendered* as a webpage at https://bids-specification.readthedocs.io.

The website is built from a GitHub repository that consists of mostly markdown files at https://github.com/bids-standard/bids-specification.
If you don't know much about markdown, here's a [good intro guide](https://guides.github.com/features/mastering-markdown/)

The file that you are most likely to propose changes to is [src/03-modality-agnostic-files.md](https://github.com/bids-standard/bids-specification/blob/master/src/03-modality-agnostic-files.md), although there may be additional changes that have to happen in other pars of the repository

-----------------------

## BIDS-prov in the NIDM project
The Neuroimaging Data Model (NIDM) is a collection of specification documents that define extensions the `W3C PROV` standard for the domain of human brain mapping

<center>
<img src="img/nidm-layer-cake.png" width="80%" position="center">
</center>

BIDS-prov takes effect at level 1 in the set of layers presented above. It follows semantics web practices (level 0) to allow for expression of arbitrary interactions between Agents, Entities and Activites, as defined in the W3C documentation.

---------------
Mature building blocks of NIDM:
* [NIDM-terms](https://github.com/incf-nidash/nidm-terms)
* [NIDM-results](http://nidm.nidash.org/specs/nidm-results_130.html)

-----------
### [New features (not in the spec)](new_features.md)
