#!/usr/bin/python
# coding: utf-8

"""
A simple Nipype workflow performing brain extraction and normalisation
of an anatomical file.
"""
from os.path import abspath

from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.fsl import BET, FLIRT, Info
from nipype.interfaces.io import ExportFile

# Create workflow
workflow = Workflow(name='bids_prov_workflow')
workflow.base_dir = abspath('derivatives/')

# Create nodes
brain_extraction = Node(BET(), name = 'brain_extraction')
brain_extraction.inputs.in_file = abspath('sub-001/anat/sub-001_T1w.nii.gz')

normalization = Node(FLIRT(), name = 'normalization')
normalization.inputs.reference = Info.standard_image('MNI152_T1_1mm_brain.nii.gz')
workflow.connect(brain_extraction, 'out_file', normalization, 'in_file')

export_brain = Node(ExportFile(), name = 'export_brain')
export_brain.inputs.clobber = True
export_brain.inputs.out_file = abspath(
	'derivatives/normalize/sub-001/anat/sub-001_T1w_brain.nii.gz')
workflow.connect(brain_extraction, 'out_file', export_brain, 'in_file')

export_normalized_brain = Node(ExportFile(), name = 'export_normalized_brain')
export_normalized_brain.inputs.clobber = True
export_normalized_brain.inputs.out_file = abspath(
	'derivatives/normalize/sub-001/anat/sub-001_space-mni152nlin2009casym_T1w_brain.nii.gz')
workflow.connect(brain_extraction, 'out_file', export_normalized_brain, 'in_file')

# Run workflow
workflow.run()
