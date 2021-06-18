import click
import re
import sys
from collections import defaultdict
from itertools import chain
import json
import os
from typing import List, Mapping, Tuple

import random
import string

from . import fsl_config as conf


def get_id(size=10):
    """get a random id as a string of `size` characters"""
    return "".join(random.choice(string.ascii_letters) for i in range(size))


# regex to catch inputs
# in `cp /fsl/5.0/doc/fsl.css .files no_ext 5.0` --> only `.files` should match
INPUT_RE = r"([\/\w\.\?-]{3,}\.?[\w]{2,})"
ATTRIBUTE_RE = r"(-+[a-zA-Z_]+)[\s|=]?([\/a-zA-Z._\d]+)?"

# tags used to detect inputs from command lines
# eg. `/usr/share/fsl/5.0/bin/film_gls --in=filtered_func_data`
INPUT_TAGS = frozenset(
    [
        "-in",
        "-i",
        "[INPUT_FILE]",  # sepcific to bet2
        # "-r",  # `cp -r` --> recursrive ???
    ]
)

# tags used to detect outputs from cammand lines
# eg. convert_xfm -inverse -omat highres2example_func.mat example_func2highres.mat
OUPUT_TAGS = frozenset(
    [
        "-o",
        "-omat",
    ]
)


def readlines(filename: str) -> Mapping[str, List[str]]:
    """read a file containing command lines

    Example
    -------
    with a file containing
    ```bash
    #### Feat main script

    /bin/cp /tmp/feat_oJmMLg.fsf design.fsf
    /usr/share/fsl/5.0/bin/feat_model design
    mkdir .files;cp /usr/share/fsl/5.0/doc/fsl.css .files
    ```

    we will obtain
    ```python
    {
        ' Feat main script': [
            '/bin/cp /tmp/feat_oJmMLg.fsf design.fsf',
            '/usr/share/fsl/5.0/bin/feat_model design',
            'mkdir .files',
            'cp /usr/share/fsl/5.0/doc/fsl.css .files'
        ]
    }
    ```
    """
    res = defaultdict(list)
    with open(filename) as fd:
        lines = fd.readlines()
        n_line = 0
        while n_line < len(lines):
            line = lines[n_line][:-1]
            # TODO : add </pre> as in
            # https://github.com/incf-nidash/nidmresults-examples/blob/master/fsl_gamma_basis/logs/feat2_pre
            if line.startswith("#"):
                key = line.replace("#", "")
                cmds, i = read_commands(lines[n_line + 1 :])
                n_line += i
                if cmds:
                    res[key].extend(cmds)
            else:
                n_line += 1
    return dict(res)


def read_commands(lines: List[str]) -> Tuple[List[str], int]:
    """group_commands

    Mainly does
    1. Iter on `lines`, until it reaches a `\n`
    2. Explode commands defined on the same line, so they can be treated separately

    Returns
    -------
    The next group of commands, and the index at which it stops
    """
    res = list()
    i = 0
    for line in lines:
        if re.match(r"^[a-z/].*$", line):
            res.extend(line[:-1].split(";"))
        elif line == "\n":
            pass
        else:
            break
        i += 1
    return res, i


def get_closest_config(key):
    """
    get the FSL config from bosh if possible, trying to match names
    of executables returned from bosh with subparts of `key`

    Example
    -------
    ```pytthon
    >>> stats_conf = get_closest_confif("fslstats")
    >>> stats_conf["version"]
    5.0.9
    ```
    """
    key = re.sub("\d", "", key)
    if not key:
        return None
    key = next((k for k in conf.bosh_config.keys() if (k in key or key in k)), None)
    if key is not None:
        return conf.bosh_config[key]
    return None


def build_records(groups: Mapping[str, List[str]], records=defaultdict(list)):
    """
    Build the `records` field for the final .jsonld file,
    from commands lines grouped by stage (eg. `Registration`, `Post-stats`)

    Returns
    -------
    dict: a set of records compliant with the BIDS-prov standard
    """
    for k, v in groups.items():
        group_name = k.lower().replace(" ", "_")
        group_activity_id = f"niiri:{group_name}_{get_id(5)}"
        records["prov:Activity"].append(
            {
                "@id": group_activity_id,
                "label": group_name,
                "wasAssociatedWith": "RRID:SCR_002823",
            }
        )

        for cmd in v:
            cmd_s = cmd.split(" ")
            a_name = cmd_s[0]
            if a_name.endswith(":"):  # result of `echo`
                continue

            attributes = defaultdict(list)

            # same key can have multiple value
            for key, value in re.findall(ATTRIBUTE_RE, cmd):
                attributes[key].append(value)

            # make sure attributes are not considered as entities
            cmd = re.sub(ATTRIBUTE_RE, "", cmd)

            inputs = list(
                chain(*(attributes.pop(k) for k in attributes.keys() & INPUT_TAGS))
            )
            outputs = list(
                chain(*(attributes.pop(k) for k in attributes.keys() & OUPUT_TAGS))
            )
            entity_names = [_ for _ in re.findall(INPUT_RE, cmd[len(a_name) :])]
            cmd_conf = get_closest_config(a_name)
            if cmd_conf:
                pos_args = filter(
                    lambda e: not e.startswith("-"), cmd_s
                )  # TODO use "-key value" mappings
                _map = dict(zip(cmd_conf["command-line"].split(" "), pos_args))
                inputs += [_map[i] for i in INPUT_TAGS if i in _map]

            elif entity_names and entity_names[0] in cmd:
                outputs.append(entity_names[-1])
                if len(entity_names) > 1:
                    inputs.append(entity_names[0])

            label = f"{group_name}_{os.path.split(a_name)[1]}"
            a = {
                "@id": f"niiri:{label}_{get_id(5)}",
                "label": label,
                "wasAssociatedWith": "RRID:SCR_002823",
                "attributes": [
                    (k, v if len(v) > 1 else v[0]) for k, v in attributes.items()
                ],
                "used": list(),
                "prov:wasInfluencedBy": group_activity_id,
            }

            input_id = ""
            for input_path in inputs:
                input_name = input_path.replace("/", "_")
                input_id = f"niiri:{get_id(size=5)}_{input_name}"  # def format_id

                existing_input = next(
                    (
                        _
                        for _ in records["prov:Entity"]
                        if _["prov:atLocation"] == input_path
                    ),
                    None,
                )
                if existing_input is None:
                    e = {
                        "@id": input_id,  # TODO : uuid
                        "label": os.path.split(input_path)[1],
                        "prov:atLocation": input_path,
                    }
                    records["prov:Entity"].append(e)
                    a["used"].append(input_id)
                else:
                    a["used"].append(existing_input["@id"])

            for output_path in outputs:
                output_name = output_path.replace("/", "_")
                records["prov:Entity"].append(
                    {
                        "@id": f"niiri:{get_id(size=5)}_{output_name}",
                        "label": os.path.split(output_path)[1],
                        "prov:atLocation": output_name,
                        "wasGeneratedBy": a["@id"],
                        "derivedFrom": input_id,  # FIXME currently last input ID
                    }
                )

            records["prov:Activity"].append(a)
    return dict(records)


@click.command()
@click.argument("filenames", nargs=-1)
@click.option("--output-file", "-o", required=True)
@click.option(
    "--context-url",
    "-c",
    default=conf.DEFAULT_CONTEXT_URL,
)
def fsl_to_bids_pros(filenames, output_file, context_url):
    filename = filenames[0]  # FIXME

    graph = conf.get_default_graph(context_url)

    lines = readlines(filename)
    records = build_records(lines)
    graph["records"].update(records)

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=2)


if __name__ == "__main__":
    sys.exit(fsl_to_bids_pros())
