# Freesurfer Segmentation Statistics Export Example

This example is derived from our [NIDM representations of ABIDE-1 BIDS data](https://github.com/dbkeator/simple2_NIDM_examples/tree/master/datasets.datalad.org/abide/RawDataBIDS).  
Along with the BIDS data conversion to NIDM we added Freesurfer-derived segmentation statistics (and segmentations using FSL and ANTS).  The jsonld provenance example included here
was taken from the CMU_A site NIDM jsonld file and modified to be more BIDS-Prov like based on the current extension documentation.  Note, I've only kept the 
prov:Activity and prov:Agent (software agent) from the original NIDM jsonld file.  The NIDM jsonld file also includes a prov:Entity, containing the actual volume and other statistics
for each participant,  which is prov:wasDerivedFrom the prov:Activity shown in
this example.

In this example, I didn't parse up the freesurfer:cmdline to separate out all the parameters.  I wasn't sure yet how to format that in BIDS-Prov.  

In case you don't like to read jsonld files, you can see a visualization [here](https://drive.google.com/file/d/1mwhcetcJMT-1CwghJZ1_ILnaXEiPaDmw/view?usp=sharing).
