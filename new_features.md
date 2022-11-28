### New features

List of all features you can find in `examples/*.json` files, but are not mentionned in [the spec](https://docs.google.com/document/d/1vw3VNDof5cecv2PkFp7Lw_pNUTUo8-m8V4SIdtGJVKs/edit?usp=sharing)

- [type indexing](https://w3c.github.io/json-ld-syntax/#node-type-indexing)
- Activity definitions, instead of just Agent and Entities
- Activities attributes defined via key/value list-like pairs, allowing to pass unstructured extra information
- Activities "used" field allow multiple entries : multiple entities as input
- [prov:wasInfluencedBy](https://www.w3.org/TR/prov-o/#wasInfluencedBy) to represent inplace edition of an entity, instead of outputting a new entity (a new "state" of the former entity) and a new Activity corresponding to the edition. This is to encourage human readable representations, as the number of nodes is reduced.
