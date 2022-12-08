from bids_prov.spm_parser import spm_to_bids_prov
from bids_prov.visualize import main as visualize

import os
import shutil
import argparse
from bids_prov import spm_load_config as conf
import git


def main():
    """
    Launch all batch.m in a relative folder opt.data_dir, export jsonld + png in output_dir
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--input_dir", type=str, default=None, help="data dir where batch.m are researched")
    parser.add_argument("--output_dir", type=str, default="results", help="output dir where results are written")
    parser.add_argument("--verbose", action="store_true", help="more print")

    opt = parser.parse_args()

    if opt.input_dir is None:
        if os.path.exists("nidmresults-examples"):
            opt.input_dir = "nidmresults-examples"
        else:
            print("Fetching nidmresults-examples...")
            git.Git().clone("https://github.com/incf-nidash/nidmresults-examples")
            opt.input_dir = "nidmresults-examples"
            print("Fetch done.")

    if os.path.exists(opt.output_dir):
        shutil.rmtree(opt.output_dir)
    os.makedirs(opt.output_dir, exist_ok=True)

    print("Processing files...")
    for root, dirs, files in os.walk(opt.input_dir):
        for file in files:
            # matlab extension the one of your choice.
            if file.endswith("batch.m"):
                print("    file=", root + "/" + str(file))
                output_file_base = root.split("/")[-1]
                filename = root + "/" + str(file)
                shutil.copyfile(filename, opt.output_dir + "/" + output_file_base + "_batch.m")

                spm_to_bids_prov(
                    root + "/" + str(file),
                    conf.CONTEXT_URL,
                    output_file=opt.output_dir + "/" + output_file_base + ".jsonld",
                    verbose=opt.verbose,
                )

                visualize(
                    opt.output_dir + "/" + output_file_base + ".jsonld",
                    output_file=opt.output_dir + "/" + output_file_base + ".png",
                )
    print(f"End of processed files. Results in dir : '{opt.output_dir}'")


if __name__ == "__main__":
    main()
    # main('./nidm-examples', './nidm-results')
