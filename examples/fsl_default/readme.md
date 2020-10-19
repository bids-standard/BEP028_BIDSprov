## workflow for "Feat 1 Practical" example

---

### Steps

Tutorial available [here](https://fsl.fmrib.ox.ac.uk/fslcourse/lectures/practicals/feat1/index.html)

---

### Workflow

<center>
<img src="fsl_default.png" width="90%" position="center">
</center>

---

### Docker

[This image](https://hub.docker.com/r/vistalab/fsl-v5.0) was used to reproduce experiments

### Generate a graph

from the root of this project

```bash
python bids_prov/visualize.py examples/fsl_default/default.json examples/fsl_default/single_subject_inference.json -o fsl_default.png
```

generate the graph dedicated to single subject inference, and skips details regarding group analysis (contained in `examples/fsl_default/group_analysis.json`)
