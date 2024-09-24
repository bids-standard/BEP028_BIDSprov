#!/usr/bin/env python

import argparse
import os
import random
import shutil
from datetime import datetime

from bids_prov.afni.afni_parser import afni_to_bids_prov
from bids_prov.fsl.fsl_parser import fsl_to_bids_prov
from bids_prov.spm.spm_parser import spm_to_bids_prov
from bids_prov.utils import CONTEXT_URL
from bids_prov.visualize import main as visualize

def clean_spm_paths(spm_file):
    """Remove parts of file paths contained in a nidm-example spm batch.m file"""

    with open(spm_file, 'r') as file:
        lines = file.readlines()

    for index, line in enumerate(lines):
        lines[index] = line.replace(
            '/storage/essicd/data/NIDM-Ex/BIDS_Data/DATA/BIDS/ds011/', 'ds011/')
        lines[index] = lines[index].replace(
            '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/', 'ds011/derivatives/')

    with open(spm_file, 'w') as file:
        for line in lines:
            file.write(line)

def process_file(context_write, root, file, filename_ss_ext, output_dir, parser_function, verbose, with_blocks=False):
    """Process a file using the given parser function and save the output to the output directory."""

    context_write.write(f"    file= {root}/{str(file)}\n")
    filename = root + "/" + str(file)
    if with_blocks is False:
        shutil.copyfile(filename, output_dir + "/" + str(file))

    if 'spm' in output_dir:
        clean_spm_paths(output_dir + "/" + str(file))

    output_base = output_dir + "/" + filename_ss_ext if with_blocks is False else output_dir + "/" + filename_ss_ext + "_block"
    output_jsonld = output_base + ".jsonld"
    output_png = output_base + ".png"

    if parser_function != afni_to_bids_prov:
        jsonld_same_as_existing = parser_function(root + "/" + str(file), CONTEXT_URL,
                                                  output_file=output_jsonld, verbose=verbose)
    else:
        jsonld_same_as_existing = parser_function(root + "/" + str(file), CONTEXT_URL,
                                                  output_file=output_jsonld, verbose=verbose, with_blocks=with_blocks)

    if not jsonld_same_as_existing:  # do not generate the png if the jsonld has not evolved
        visualize(output_jsonld, output_file=output_png)


def main():
    """
    Parse a set of files located (.m for SPM12, .html for fsl and .sub_001 for afni) in the same directory (input_directory) to the
    bids-prov standard in an output directory (output_directory).

    Parameters
    --input_dir : str
        The directory where the .m and .html files are located. Default: "nidmresults-examples".
    --output_dir : str
        The directory where the results will be written. Default: "results".
    --verbose : bool
        If True, more information will be printed during the processing.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default="nidmresults-examples",
                        help="data dir where .m and .html are researched")
    parser.add_argument("--output_dir", type=str, default="examples",
                        help="output dir where results are written")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    # fix the seed to have identical jsonlds if there are no other modifications
    random.seed(14)

    os.makedirs(opt.output_dir, exist_ok=True)
    output_dir_spm = opt.output_dir + "/spm"
    output_dir_fsl = opt.output_dir + "/fsl"
    output_dir_afni = opt.output_dir + "/afni"
    os.makedirs(output_dir_spm, exist_ok=True)
    os.makedirs(output_dir_fsl, exist_ok=True)
    os.makedirs(output_dir_afni, exist_ok=True)

    # each time, deleting the context file
    for filename in os.listdir(opt.output_dir):
        if filename.startswith("context_"):
            os.remove(os.path.join(opt.output_dir, filename))

    # Context file
    start_time = datetime.now()
    start_time_format = "{:%Y_%m_%d_%Hh%Mm%Ss}".format(start_time)
    context_file = f"{opt.output_dir}/context_{start_time_format}.txt"
    context_write = open(context_file, "w")
    context_write.write(f"Date : {start_time_format}\n")
    context_write.write("Processing files...\n")

    # Iteration on each example
    for root, _, files in sorted(os.walk(opt.input_dir)):
        for file in sorted(files):

            if file.endswith("batch.m"):  # spm
                filename_ss_ext = file.split(".m")[0]
                process_file(context_write, root, file, filename_ss_ext, output_dir_spm, spm_to_bids_prov, opt.verbose)

            elif file.endswith("report_log.html"):  # fsl
                filename_ss_ext = file.split(".html")[0]
                process_file(context_write, root, file, filename_ss_ext, output_dir_fsl, fsl_to_bids_prov, opt.verbose)

            elif file.endswith("proc.sub_001") or file.endswith(".tcsh"):  # afni
                if ".sub_001" in file:
                    filename_ss_ext = file.split(".sub_001")[0]
                else:
                    filename_ss_ext = file.split(".tcsh")[0]
                process_file(context_write, root, file, filename_ss_ext, output_dir_afni, afni_to_bids_prov, opt.verbose)
                # afni block
                process_file(context_write, root, file, filename_ss_ext, output_dir_afni, afni_to_bids_prov, opt.verbose, with_blocks=True)

            else:
                print(" -> Extension of file ", file, " not supported")
                continue

    context_write.write(f"End of processed files. Results in dir : '{opt.output_dir}'. "
                        f"Time required: {datetime.now() - start_time}\n")


if __name__ == "__main__":
    main()
