# BEP028
This repository contains **BIDS Extension Proposal 028 : BIDS-prov, a provenance framework for BIDS**.

## Our goal
**Interpreting and comparing scientific results** and enabling reusable data and analysis output require understanding provenance, i.e. how the data were generated and processed. To be useful, the provenance must be understandable, easily communicated, and captured automatically in machine accessible form. Provenance records are thus used to encode transformations between digital objects.

### Who is building BEP 028  ✨

Camille Maumet ([@cmaumet](https://github.com/cmaumet)) and Satrajit Ghosh ([@satra](https://github.com/satra)) are the BEP co-moderators. Here is the list of all contributors ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

- Camille Maumet ([@cmaumet](https://github.com/cmaumet))<a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=cmaumet" title="Code">💻</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/pulls?q=is%3Apr+reviewed-by%3Acmaumet" title="Reviewed Pull Requests">👀</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=cmaumet" title="Documentation">📖</a>
<a href="https://github.com/bids-standard/BEP028_BIDSprov/issues?q=author%3Acmaumet" title="Bug reports">🐛</a><a href="#content-dorahermes" title="Content">🖋</a> <a href="#ideas-dorahermes" title="Ideas, Planning, & Feedback">🤔</a><a href="#maintenance-dorahermes" title="Maintenance">🚧</a>

- Satrajit Ghosh ([@satra](https://github.com/satra))<a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=satra" title="Code">💻</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/pulls?q=is%3Apr+reviewed-by%3Asatra" title="Reviewed Pull Requests">👀</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=satra" title="Documentation">📖</a>
<a href="https://github.com/bids-standard/BEP028_BIDSprov/issues?q=author%3Asatra" title="Bug reports">🐛</a><a href="#ideas-dorahermes" title="Ideas, Planning, & Feedback">🤔</a>

- Stefan Appelhoff ([@sappelhoff](https://github.com/sappelhoff))<a href="#ideas-dorahermes" title="Ideas, Planning, & Feedback">🤔</a>

- Chris Markiewicz ([@effigies](https://github.com/effigies))<a href="#ideas-dorahermes" title="Ideas, Planning, & Feedback">🤔</a>

- Yaroslav Halchenko ([@yarikoptic](https://github.com/yarikoptic))<a href="#ideas-dorahermes" title="Ideas, Planning, & Feedback">🤔</a>

- Jean-Baptiste Poline ([@jbpoline](https://github.com/jbpoline))<a href="#ideas-dorahermes" title="Ideas, Planning, & Feedback">🤔</a>

- Rémi Adon ([@remiadon](https://github.com/remiadon))<a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=remiadon" title="Code">💻</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/pulls?q=is%3Apr+reviewed-by%3Aremiadon" title="Reviewed Pull Requests">👀</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=remiadon" title="Documentation">📖</a>
<a href="https://github.com/bids-standard/BEP028_BIDSprov/issues?q=author%3Aremiadon" title="Bug reports">🐛</a>

- Hermann Courteille ([@hermann74](https://github.com/hermann74))<a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=hermann74" title="Code">💻</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/pulls?q=is%3Apr+reviewed-by%3Ahermann74" title="Reviewed Pull Requests">👀</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=hermann74" title="Documentation">📖</a>
<a href="https://github.com/bids-standard/BEP028_BIDSprov/issues?q=author%3Ahermann74" title="Bug reports">🐛</a>

- Thomas Betton ([@thomasbtnfr](https://github.com/thomasbtnfr))<a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=thomasbtnfr" title="Code">💻</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/pulls?q=is%3Apr+reviewed-by%3Athomasbtnfr" title="Reviewed Pull Requests">👀</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=thomasbtnfr" title="Documentation">📖</a>
<a href="https://github.com/bids-standard/BEP028_BIDSprov/issues?q=author%3Athomasbtnfr" title="Bug reports">🐛</a>

- Cyril Regan ([@cyril-data](https://github.com/cyril-data))<a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=cyril-data" title="Code">💻</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/pulls?q=is%3Apr+reviewed-by%3Acyril-data" title="Reviewed Pull Requests">👀</a><a href="https://github.com/bids-standard/BEP028_BIDSprov/commits?author=cyril-data" title="Documentation">📖</a>
<a href="https://github.com/bids-standard/BEP028_BIDSprov/issues?q=author%3Acyril-data" title="Bug reports">🐛</a>

This project follows the
[all-contributors](https://github.com/all-contributors/all-contributors)
specification. Contributions of any kind welcome!


### BIDS-prov in the NIDM project

The Neuroimaging Data Model (NIDM) is a collection of specification documents that define extensions the `W3C PROV` standard for the domain of human brain mapping.

<p align="center">
  <img width="50%" src="img/nidm-layer-cake.png">
</p>

BIDS-prov is a BIDS extension that is compatible with NIDM.



## How to help
[Our goal](#our-goal) is to extends BIDS to be able to track provenance at every stage of an experiment.

For this purpose we have to **propose changes to the BIDS specification**.

The BIDS specification is *rendered* as a webpage at https://bids-specification.readthedocs.io.

The website is built from a GitHub repository that consists of mostly markdown files at https://github.com/bids-standard/bids-specification.
If you don't know much about markdown, here's a [good intro guide](https://guides.github.com/features/mastering-markdown/).


## Finding information and getting in touch

### Google doc
The BEP028 is in a [google doc](https://docs.google.com/document/d/1vw3VNDof5cecv2PkFp7Lw_pNUTUo8-m8V4SIdtGJVKs/edit?usp=sharing).

### Contact BIDS-Prov
The group is always open to new contributors interested in neuroimaging data sharing. 
To participate in discussions or to ask any question, please email us at **incf-nidash-nidm@googlegroups.com**.

## Additional resources
Mature building blocks of NIDM:
* [NIDM-terms](https://github.com/incf-nidash/nidm-terms)
* [NIDM-results](http://nidm.nidash.org/specs/nidm-results_130.html)


[New features (to be included)](new_features.md)


## Run parsers on the SPM, FSL and AFNI data

To obtain data in **bids-prov format**, you can use the developed parsers.
* [Tutorial](https://github.com/bids-standard/BEP028_BIDSprov/blob/master/bids_prov/README.md)


## Code of conduct
We are committed to building a welcoming and harrasement free experience for all our contributors. As a contributor to the BIDS-Prov specification, we ask you to follow our [code of conduct](code_of_conduct.md)


_Credits: This README was build based on the [BEP001 README](https://github.com/bids-standard/bep001/blob/master/README.md)._
