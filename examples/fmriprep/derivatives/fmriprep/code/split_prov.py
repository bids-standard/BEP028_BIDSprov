#!/usr/bin/python
# coding: utf-8

""" Split JSON-LD provenance into several JSON files, and sidecar JSONs.
    Note that the script does not create (sub)directories.
"""

from argparse import ArgumentParser
import json
from pathlib import Path
from os.path import join, isfile

def keep_after_pattern(text: str, pattern: str) -> str:
    """ Keep the part of input text that is after the given pattern.
        This doesn't work if the pattern appears several times in the text.

        Arguments:
            - text, str: the input text to split
            - pattern, str: a pattern to find in the text

        Return:
            - str: the part of text after the given pattern
    """
    if pattern in text:
        return text.split(pattern, 1)[1]
    return None

def get_sidecar_path(path: str) -> str:
    """ From a data file path inside a BIDS dataset,
        return the path to its corresponding sidecar JSON.

        Arguments:
            - path, str: path to the data file

        Return:
            - str: the path to the sidecar JSON
    """
    path_object = Path(path)
    parent_path_object = path_object.parent
    if '.gz' in path_object.suffixes:
        return parent_path_object.joinpath(Path(path_object.stem).stem+'.json')
    return parent_path_object.joinpath(path_object.stem+'.json')

# Parse arguments
argument_parser = ArgumentParser()
argument_parser.add_argument(
    '-i', '--input_file', type=str,
    required=True, help='JSON-LD file containing provenance records')
argument_parser.add_argument(
    '-o', '--output_dir', type=str,
    required=True, help='Output directory, root of derivatives dataset')
argument_parser.add_argument(
    '-p', '--filename_pattern', type=str, default='out/fmriprep/',
    help='Only extract Entities containing this pattern in their label')
arguments = argument_parser.parse_args()

# Load main JSON-LD file
records = {}
with open(arguments.input_file, 'r', encoding='utf-8') as file:
    records = json.load(file)

# Loop through entities
for entity in records['Records']['Entities']:

    # Get Label field(s)
    label = entity['Label']
    if not isinstance(label, list):
        label = [label]

    # Get GeneratedBy field(s)
    generated_by = []
    if 'GeneratedBy' in entity:
        generated_by = entity['GeneratedBy']
        if not isinstance(generated_by, list):
            generated_by = [generated_by]

    # If entity Label is inside `out/fmriprep/`
    for label_element, gb_element in zip(label, generated_by):

        # Get Label relative path
        relative_path_entity = keep_after_pattern(label_element, arguments.filename_pattern)
        if relative_path_entity:
            data_path = join(arguments.output_dir, relative_path_entity)
            sidecar_path = join(arguments.output_dir, get_sidecar_path(relative_path_entity))

            # Create sidecar if needed
            if not isfile(sidecar_path):
                Path(sidecar_path).touch()
            if Path(sidecar_path).stat().st_size == 0:
                with open(sidecar_path, 'w', encoding='utf-8') as file:
                    file.write('{}\n')

            # Create datafile if needed
            if not isfile(data_path):
                Path(data_path).touch()


            # Read file, add  GeneratedBy field
            contents = {}
            with open(sidecar_path, 'r', encoding='utf-8') as file:
                contents = json.load(file)

            contents['GeneratedBy'] = gb_element                
            with open(sidecar_path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(contents, indent=4))
