## Contributing guidelines


### Structure of a proposal
Here is how a proposal should be structured for easier reviewing and discussions

* Proposal and rationale behind this
* An example and its dedicated subfolder in the `examples/` folder


### Avoid big pull requests

We could do all our work in a branch of the main [bids-specification](https://github.com/bids-standard/bids-specification) repository.
We would be able to see how our proposed changes affected the current version of the specification by opening a [pull request](https://help.github.com/articles/about-pull-requests/).

However, there are quite a few changes to make, and quite a lot of conversation to have around each of them, so our proposed way of working is to **break up the individual changes into manageable chunks**.

Each conceptual update to the specification should have a *``proposal file``*.
This file should explain what change it is proposing and provide a justification for the change.

Once the proposal is ready, the developer should **open a pull request** to the master branch of the BEP028 repository (this one).
If everyone agrees on the proposal, the file will be merged to master.

(There will then be some wrangling to make the one big pull request to the bids-specification.
We'll cross that bridge when we come to it! :sparkles:)
