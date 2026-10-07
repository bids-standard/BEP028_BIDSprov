#!/usr/bin/python
# coding: utf-8

""" Main command line tool for all bids_prov executables. """

from argparse import ArgumentParser

from bids_prov.merge import entry_point as merge
from bids_prov.extract import entry_point as extract
from bids_prov.visualize import entry_point as visualize

def entry_point():
    """ Parse command line arguments for the bids_prov command """

    parser = ArgumentParser(
        prog='bids_prov',
        description='One command line tool for all BIDS-Prov executables.')
    sub_commands = parser.add_subparsers(dest='sub_command',
        help='One of these subcommands is required.', required=True)

    # Parser for the merge command
    parser_merge = sub_commands.add_parser('merge',
        help='Merge all provenance metadata from a BIDS dataset into one JSON-LD file.')
    parser_merge.add_argument('--dataset', '-d', type=str, default='.',
        help='The path to the input BIDS dataset. Do not provide this argument if the\
        dataset is in the current directory.')
    parser_merge.add_argument('--derivative', action='store_true',
        help='Set this option to specify the dataset is a BIDS derivative dataset.')
    parser_merge.add_argument('--output_file', '-o', type=str, required=True,
        help='Name for the output JSON-LD file containing the provenance graph for the input dataset.')
    parser_merge.add_argument('--entity', '-e', type=str,
        help='`prov-` BIDS entity for which to extract the metadata. E.g.: for `prov-spm`, provide "-e spm"')

    # Parser for the extract command
    parser_extract = sub_commands.add_parser('extract',
        help='Generate the subgraph containing ancestors to a given node.')
    parser_extract.add_argument('--input_file', '-i', type=str, required=True,
        help='Complete graph as a JSON-LD file.')
    parser_extract.add_argument('--node_id', '-n', type=str, required=True,
        help='Identifier for the starting node.')
    parser_extract.add_argument('--output_file', '-o', type=str, required=True,
        help='Name for the output JSON-LD file containing the subgraph.')

    # Parser for the visualize command
    parser_visualize = sub_commands.add_parser('visualize',
        help='Generate a `graphviz` graph as PNG file from BIDS-Prov data in a JSON-LD file')
    parser_visualize.add_argument('--input_file', '-i', type=str, required=True,
        help='Input BIDS-Prov data as a JSON-LD file.')
    parser_visualize.add_argument('--output_file', '-o', type=str,
        help='Name for the output PNG file showing the `graphviz` graph.\
        If not provided, the input name stem will be used for the output file name.')
    parser_visualize.add_argument('--detailed', '-d', action='store_true',
        help='Set this option to write a detailed version of the graph.')

    # Parse command line and launch corresponding programs
    args = parser.parse_args()
    match args.sub_command:
        case 'merge':
            merge(args.dataset, args.derivative, args.output_file, args.entity)
        case 'extract':
            extract(args.input_file, args.node_id, args.output_file)
        case 'visualize':
            visualize(args.input_file, args.output_file, args.detailed)
        case _:
            return
