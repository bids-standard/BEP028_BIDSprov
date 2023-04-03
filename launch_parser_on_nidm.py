import os
import shutil
import argparse
import random
from datetime import datetime

from bids_prov.afni.afni_parser import afni_to_bids_prov
from bids_prov.spm.spm_parser import spm_to_bids_prov
from bids_prov.fsl.fsl_parser import fsl_to_bids_prov
from bids_prov.visualize import main as visualize
from bids_prov.utils import CONTEXT_URL

def main():
    """
    Parse a set of files located (.m for SPM12 and .html for fsl) in the same directory (input_directory) to the
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

    random.seed(1)

    opt = parser.parse_args()

    os.makedirs(opt.output_dir, exist_ok=True)

    output_dir_spm = opt.output_dir + "/spm"
    output_dir_fsl = opt.output_dir + "/fsl"
    output_dir_afni = opt.output_dir + "/afni"
    os.makedirs(output_dir_spm, exist_ok=True)
    os.makedirs(output_dir_fsl, exist_ok=True)
    os.makedirs(output_dir_afni, exist_ok=True)

    for filename in os.listdir(opt.output_dir):
        if filename.startswith("context_"):
            os.remove(os.path.join(opt.output_dir, filename))

    start_time = datetime.now()
    start_time_format = "{:%Y_%m_%d_%Hh%Mm%Ss}".format(start_time)
    context_file = f"{opt.output_dir}/context_{start_time_format}.txt"
    context_write = open(context_file, "w")
    context_write.write(f"Date : {start_time_format}\n")

    context_write.write("Processing files...\n")

    for root, dirs, files in os.walk(opt.input_dir):
        for file in files:
            jsonld_same_as_existing = False

            # matlab extension the one of your choice.
            if file.endswith("batch.m"):
                context_write.write(f"    file= {root}/{str(file)}\n")
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".m")[0]
                shutil.copyfile(filename, output_dir_spm + "/" + str(file))
                output_jsonld = output_dir_spm + "/" + filename_ss_ext + ".jsonld"
                jsonld_same_as_existing = spm_to_bids_prov(root + "/" + str(file), CONTEXT_URL,
                                                           output_file=output_jsonld, verbose=opt.verbose)
                output_png = output_dir_spm + "/" + filename_ss_ext + ".png"

            elif file.endswith("report_log.html"):
                context_write.write(f"    file= {root}/{str(file)}\n")
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".html")[0]
                shutil.copyfile(filename, output_dir_fsl + "/" + str(file))
                output_jsonld = output_dir_fsl + "/" + filename_ss_ext + ".jsonld"
                jsonld_same_as_existing = fsl_to_bids_prov(root + "/" + str(file), CONTEXT_URL,
                                                           output_file=output_jsonld, verbose=opt.verbose)
                output_png = output_dir_fsl + "/" + filename_ss_ext + ".png"

            elif file.endswith("proc.sub_001") or file.endswith(".tcsh"):
                context_write.write(f"    file= {root}/{str(file)}\n")
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".sub_001")[0]
                shutil.copyfile(filename, output_dir_afni + "/" + str(file))
                output_jsonld = output_dir_afni + "/" + filename_ss_ext + ".jsonld"
                jsonld_same_as_existing = afni_to_bids_prov(root + "/" + str(file), CONTEXT_URL,
                                                            output_file=output_jsonld, verbose=opt.verbose)
                output_png = output_dir_afni + "/" + filename_ss_ext + ".png"

            else:
                print(" -> Extension of file ", file , " not supported")
                continue

            if not jsonld_same_as_existing:
                visualize(output_jsonld, output_file=output_png)

    context_write.write(f"End of processed files. Results in dir : '{opt.output_dir}'. "
                        f"Time required: {datetime.now() - start_time}\n")

    context_write.close()


if __name__ == "__main__":
    main()
