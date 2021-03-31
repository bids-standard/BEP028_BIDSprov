import click
import re
import sys
from collections import defaultdict
from itertools import chain
import requests
import json
import os

import prov.model as prov

import random
import string
import codecs

from . import fsl_config as conf

from difflib import SequenceMatcher

get_id = lambda size=10: "".join(
    random.choice(string.ascii_letters) for i in range(size)
)

INPUT_RE = r"([\/\w\.\?-]{3,}\.?[\w]{2,})"  # in `cp /fsl/5.0/doc/fsl.css .files no_ext 5.0` --> `cp`, `no_ext` adn `5.0` don't match
ATTRIBUTE_RE = r"(-+[a-zA-Z_]+)[\s|=]?([\/a-zA-Z._\d]+)?"

INPUT_TAGS = frozenset(
    [
        "-in",
        "-i",
        "[INPUT_FILE]",  # sepcific to bet2
        # "-r",  # `cp -r` --> recursrive ???
    ]
)

OUPUT_TAGS = frozenset(
    [
        "-o",
        "-omat",
    ]
)


def format_label(s):
    s = os.path.split(s)[1]
    # s = os.path.splitext(s)[0]
    return s


def readlines(filename):
    res = defaultdict(list)
    with open(filename) as fd:
        lines = fd.readlines()
        n_line = 0
        while n_line < len(lines):
            line = lines[n_line][:-1]
            if line.startswith(
                "#"
            ):  # TODO : add </pre> as in https://github.com/incf-nidash/nidmresults-examples/blob/master/fsl_gamma_basis/logs/feat2_pre
                key = line.replace("#", "")
                cmds, i = read_commands(lines[n_line + 1 :])
                n_line += i
                if cmds:
                    res[key].extend(cmds)
            else:
                n_line += 1
    return dict(res)


def read_commands(lines):
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
    key = re.sub("\d", "", key)
    if not key:
        return None
    key = next((k for k in conf.bosh_config.keys() if (k in key or key in k)), None)
    if key is not None:
        return conf.bosh_config[key]
    return None


def build_records(groups: dict):
    records = defaultdict(list)

    for group, (k, v) in enumerate(groups.items()):
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
            a_name, args = cmd_s[0], cmd_s[1:]
            if a_name.endswith(":"):  # result of `echo`
                continue

            attributes = defaultdict(list)
            for key, value in re.findall(
                ATTRIBUTE_RE, cmd
            ):  # same key can have multiple value
                attributes[key].append(value)

            cmd = re.sub(
                ATTRIBUTE_RE, "", cmd
            )  # make sure attributes are not considered as entities
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
                        "label": format_label(input_path),
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
                        "label": format_label(output_path),
                        "prov:atLocation": output_name,
                        "wasGeneratedBy": a["@id"],
                        "derivedFrom": input_id,  # FIXME currently last input ID
                    }
                )

            """
            for entity_name in entity_names:  # inputs and outputs
                try:
                    closest_entity = max(  # TODO filter with matching threshold
                        records["prov:Entity"],
                        key=lambda a: SequenceMatcher(
                            None, a["label"], entity_name
                        ).ratio(),
                    )
                    a["used"].append(closest_entity["@id"])
                except:
                    print(f"could not resolve entity {entity_name}")
            """
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
