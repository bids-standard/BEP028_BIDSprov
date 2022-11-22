from bids_prov.spm_parser import spm_to_bids_prov
from bids_prov.visualize import main as visualize

import os
import click
import shutil


@click.command()
@click.argument("data_dir", nargs=-1)
@click.option("--output_dir", "-o", default="result")
def main(data_dir, output_dir):
    """
    Launch all batch.m in a relative folder data_dir, export jsonld + png in output_dir
    """
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(data_dir[0]):

        for file in files:
            # matlab extension the one of your choice.
            if file.endswith("batch.m"):
                print(root + "/" + str(file))

                output_file_base = root.split("/")[-1]

                try:
                    spm_to_bids_prov(
                        [
                            root + "/" + str(file),
                            "-o",
                            output_dir + "/" + output_file_base + ".jsonld",
                        ]
                    )
                except SystemExit as err:
                    # re-raise unless spm_to_bids_prov() finished without an error
                    if err.code:
                        raise

                try:
                    visualize(
                        [
                            output_dir + "/" + output_file_base + ".jsonld",
                            "-o",
                            output_dir + "/" + output_file_base + ".png",
                        ]
                    )
                except SystemExit as err:
                    # re-raise unless main() finished without an error
                    if err.code:
                        raise


if __name__ == "__main__":
    main()
