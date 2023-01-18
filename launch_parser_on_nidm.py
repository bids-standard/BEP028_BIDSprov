import os
import shutil
import argparse
from bids_prov.spm.spm_parser import spm_to_bids_prov
from bids_prov.visualize import main as visualize
from bids_prov.fsl.fsl_parser import fsl_to_bids_prov
from bids_prov.utils import CONTEXT_URL
from datetime import datetime
import markdownify
import re


def html_to_logmd_file(htlm_file, logmd_file):
    """
    Convert an HTML file to a log markdown file.

    Parameters
    -----
    htlm_file : str
        The path of the HTML file to be converted.
    logmd_file : str
        The path of the log markdown file to be created.

    Returns
    -----
    str
    The log markdown string.

    Notes
    -----
    This function uses the markdownify package to convert the HTML to markdown.
    It also uses regular expressions to replace specific text patterns in the markdown string.

    Warning
    -----
    This function will overwrite the contents of the log markdown file if it already exists.

    Examples
    -----
    html_to_logmd_file("index.html", "log.md")
    """
    with open(htlm_file, "r") as f:
        htlm_str = f.read()
        htlm_str = re.sub("<TITLE>FSL</TITLE>", "", htlm_str)
        md = markdownify.markdownify(htlm_str, heading_style="ATX")
        logmd = re.sub("---\n\n(.*)", "## \g<1>", md)
        logmd = re.sub("Feat main script", "## Feat main script", logmd)
        logmd = re.sub("```", "", logmd)
    with open(logmd_file, "w") as f:
        f.write(logmd)
    return logmd


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

    start_time = datetime.now()
    start_time_format = "{:%Y_%m_%d_%Hh%Mm%Ss}".format(start_time)
    context_file = f"{opt.output_dir}/context_spm_{start_time_format}.txt"
    context_write = open(context_file, "w")
    context_write.write(f"Date : {start_time_format}\n")

    context_write.write("Processing files...\n")

    # SPM parser on nidm_examples
    for root, dirs, files in os.walk(opt.input_dir):
        for file in files:
            # matlab extension the one of your choice.
            if file.endswith("batch.m"):
                context_write.write(f"    file= {root}/{str(file)}\n")
                output_file_base = root.split("/")[-1]
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".m")[0]
                shutil.copyfile(filename, output_dir_spm + "/" + output_file_base + "_" + str(file))
                output_jsonld = output_dir_spm + "/" + output_file_base + "_" + filename_ss_ext + ".jsonld"
                spm_to_bids_prov(root + "/" + str(file), CONTEXT_URL, output_file=output_jsonld,
                                 verbose=opt.verbose)
                output_png = output_dir_spm + "/" + output_file_base + "_" + filename_ss_ext + ".png"
                visualize(output_jsonld, output_file=output_png)

            if file.endswith("report_log.html"):
                context_write.write(f"    file= {root}/{str(file)}\n")
                output_file_base = root.split("/")[-1]
                filename = root + "/" + str(file)
                filename_ss_ext = file.split(".html")[0]
                shutil.copyfile(filename, output_dir_fsl + "/" + output_file_base + "_" + str(file))
                output_jsonld = output_dir_fsl + "/" + output_file_base + "_" + filename_ss_ext + ".jsonld"

                logmd_file = output_dir_fsl + "/" + output_file_base + "_" + filename_ss_ext + ".md"
                html_to_logmd_file(filename, logmd_file)

                fsl_to_bids_prov(logmd_file, CONTEXT_URL, output_file=output_jsonld, verbose=opt.verbose)
                output_png = output_dir_fsl + "/" + output_file_base + "_" + filename_ss_ext + ".png"
                visualize(output_jsonld, output_file=output_png)

    context_write.write(f"End of processed files. Results in dir : '{opt.output_dir}'. "
                        f"Time required: {datetime.now()-start_time}\n")

    context_write.close()


if __name__ == "__main__":
    main()
