import os
import shutil
import argparse
from bids_prov import spm_load_config as conf
from bids_prov.spm_parser import spm_to_bids_prov
from bids_prov.visualize import main as visualize
from bids_prov.fsl_parser import fsl_to_bids_prov
from datetime import datetime
import markdownify
import re


def html_to_mdlog(htlm_str):
    htlm_str = re.sub("<TITLE>FSL</TITLE>", "", htlm_str)
    md = markdownify.markdownify(htlm_str, heading_style="ATX")
    logmd = re.sub("---\n\n(.*)", "## \g<1>", md)
    logmd = re.sub("Feat main script", "## Feat main script", logmd)
    logmd = re.sub("```", "", logmd)
    return logmd


def html_to_logmd_file(htlm_file, logmd_file):
    with open(htlm_file, "r") as f:
        htlm_str = f.read()
    logmd = html_to_mdlog(htlm_str)
    with open(logmd_file, "w") as f:
        f.write(logmd)
    return logmd


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

    output_dir_spm = opt.output_dir + "/spm"
    output_dir_fsl = opt.output_dir + "/fsl"
    os.makedirs(output_dir_spm, exist_ok=True)
    os.makedirs(output_dir_fsl, exist_ok=True)

    local_time = "{:%Y_%m_%d_%Hh%Mm%Ss}".format(datetime.now())
    context_file = f"{opt.output_dir}/context_spm_{local_time}.txt"
    context_write = open(context_file, "w")
    context_write.write(f"Date : {local_time}\n")

    print("Processing files...")
    context_write.write("Processing files...\n")

    # SPM parser on nidm_examples
    for root, dirs, files in os.walk(opt.input_dir):
        for file in files:
            # matlab extension the one of your choice.
            if file.endswith("batch.m"):
                print(f"    file= {root}/{str(file)}")
                context_write.write(f"    file= {root}/{str(file)}\n")
                output_file_base = root.split("/")[-1]
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".m")[0]
                shutil.copyfile(filename, output_dir_spm + "/" +
                                output_file_base + "_" + str(file))
                output_jsonld = output_dir_spm + "/" + \
                                output_file_base + "_" + filename_ss_ext + ".jsonld"
                spm_to_bids_prov(root + "/" + str(file), conf.CONTEXT_URL, output_file=output_jsonld,
                                 verbose=opt.verbose)
                output_png = output_dir_spm + "/" + \
                             output_file_base + "_" + filename_ss_ext + ".png"
                visualize(output_jsonld, output_file=output_png, )

            if file == "report_log.html":
                print(f"    file= {root}/{str(file)}")
                context_write.write(f"    file= {root}/{str(file)}\n")
                output_file_base = root.split("/")[-1]
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".m")[0]
                shutil.copyfile(filename, output_dir_fsl + "/" +
                                output_file_base + "_" + str(file))
                output_jsonld = output_dir_fsl + "/" + \
                                output_file_base + "_" + filename_ss_ext + ".jsonld"

                logmd_file = output_dir_fsl + "/" + output_file_base + \
                             "_" + filename_ss_ext + "_log.md"
                html_to_logmd_file(filename, logmd_file)

                fsl_to_bids_prov(logmd_file, conf.CONTEXT_URL, output_file=output_jsonld,
                                 verbose=opt.verbose)
                output_png = output_dir_fsl + "/" + \
                             output_file_base + "_" + filename_ss_ext + ".png"
                visualize(output_jsonld, output_file=output_png, )

    print(f"End of processed files. Results in dir : '{opt.output_dir}'")
    context_write.write(
        f"End of processed files. Results in dir : '{opt.output_dir}'\n")

    context_write.close()


if __name__ == "__main__":
    main()
