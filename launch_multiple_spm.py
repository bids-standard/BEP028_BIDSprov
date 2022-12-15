import os
import shutil
import argparse
from bids_prov import spm_load_config as conf
from bids_prov.spm_parser import spm_to_bids_prov
from bids_prov.visualize import main as visualize
from datetime import datetime


def main():
    """
    Launch all batch.m in a relative folder opt.data_dir, export jsonld + png in output_dir
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--input_dir", type=str, default="nidmresults-examples",
                        help="data dir where batch.m are researched")
    parser.add_argument("--output_dir", type=str, default="results",
                        help="output dir where results are written")
    parser.add_argument("--verbose", action="store_true", help="more print")

    opt = parser.parse_args()

    if os.path.exists(opt.output_dir):
        shutil.rmtree(opt.output_dir)
    os.makedirs(opt.output_dir, exist_ok=True)

    local_time = "{:%Y_%m_%d_%Hh%Mm%Ss}".format(datetime.now())
    context_file = f"{opt.output_dir}/context_spm_{local_time}.txt"
    context_write = open(context_file, "w")
    context_write.write(f"Date : {local_time}\n")

    print("Processing files...")
    context_write.write("Processing files...\n")

    for root, dirs, files in os.walk(opt.input_dir):
        for file in files:
            # matlab extension the one of your choice.
            if file.endswith("batch.m"):
                print(f"    file= {root}/{str(file)}")
                context_write.write(f"    file= {root}/{str(file)}\n")

                output_file_base = root.split("/")[-1]
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".m")[0]
                shutil.copyfile(filename, opt.output_dir + "/" +
                                output_file_base + "_" + str(file))
                output_jsonld = opt.output_dir + "/" + \
                    output_file_base + "_" + filename_ss_ext + ".jsonld"

                spm_to_bids_prov(root + "/" + str(file), conf.CONTEXT_URL, output_file=output_jsonld,
                                 verbose=opt.verbose)
                output_png = opt.output_dir + "/" + \
                    output_file_base + "_" + filename_ss_ext + ".png"

                visualize(output_jsonld, output_file=output_png,)

    print(f"End of processed files. Results in dir : '{opt.output_dir}'")
    context_write.write(
        f"End of processed files. Results in dir : '{opt.output_dir}'\n")
    context_write.close()


if __name__ == "__main__":
    main()
    # main('./nidm-examples', './nidm-results')
