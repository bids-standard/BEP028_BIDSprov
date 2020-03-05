# BIDS-prov
provenance framework for BIDS


## BIDS-prov in the NIDM project
The Neuroimaging Data Model (NIDM) is a collection of specification documents that define extensions the `W3C PROV` standard for the domain of human brain mapping

![NIDM](img/nidm-layer-cake.png "NIDM building blocks")

BIDS-prov takes effect at level 1 in the set of layers presented above. It follows semantics web practices (level 0) to allow for expression of arbitrary interactions between Agents, Entities and Activites, as defined in the W3C documentation.

Common definition and objects are directly taken from NIDM core vocab (level 2) in order to ensure all described projects speak a common language.

---------------
Mature building blocks of NIDM:
* [NIDM-terms](https://github.com/incf-nidash/nidm-terms)
* [NIDM-results](http://nidm.nidash.org/specs/nidm-results_130.html)

--------------
### Concepts 
BIDS-prov represents interactions in neuro_imaging projects using [JSON-ld](https://json-ld.org/) files, following [W3C-prov] concepts 
![NIDM](img/w3c.svg)

As an example, I may use the SPM software to run a bunch of experiments. These experiments consume files and produce files.
In this case:
* SPM is an agent
* my output files are entities, derived from some input files
* Running my SPM batch on some input files is an Activity.

