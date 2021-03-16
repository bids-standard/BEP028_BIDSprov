import click
import re
import sys
from collections import defaultdict
import requests
import json
import os

import prov.model as prov

import random
import string

from . import fsl_config as conf

from difflib import SequenceMatcher

get_id = lambda size=10: "".join(
    random.choice(string.ascii_letters) for i in range(size)
)

PARAM_RE = r"-*([a-zA-Z_]+)[\s=]+([a-zA-Z\d\\._]+)"


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
            a_name = cmd.split(" ", 1)[0]
            if "bet" in a_name:
                import pdb

                pdb.set_trace()
            if a_name.endswith(":"):  # result of `echo`
                continue
            a_name = os.path.split(a_name)[1]
            cmd_conf = get_closest_config(a_name)
            if cmd_conf:
                conf_inputs = [
                    _.get("command-line-flag")
                    for _ in cmd_conf["inputs"]
                    if "command-line-flag" in _
                ]
            else:
                cmd_conf = None
            params = re.findall(PARAM_RE, cmd)
            cmd = re.sub(PARAM_RE, "", cmd)  # remove params
            params.extend(re.findall(r"-{1,2}([a-z\d_\.]+)", cmd))  # add --[option]
            entity_names = re.findall(r"(\/?[^ ]*\.[\w:]+)", cmd)

            label = f"{group_name}_{a_name}"
            a = {
                "@id": f"niiri:{label}_{get_id(5)}",
                "label": label,
                "wasAssociatedWith": "RRID:SCR_002823",
                "attributes": list(),
                "used": list(),
                "prov:wasInfluencedBy": group_activity_id,
            }
            for p in params:
                a["attributes"].append(p)

            for entity_name in entity_names:
                e_id = f"niiri:{get_id(size=5)}_{entity_name.replace('/', '_')}"
                e = {
                    "@id": e_id,  # TODO : uuid
                    "label": entity_name,
                    "prov:atLocation": entity_name,
                    "derivedFrom": "TODO",
                }
                if entity_name == entity_names[-1]:  # output
                    e["wasGeneratedBy"] = a[
                        "@id"
                    ]  # wasAffectedBy if entity is ther result of an intermediate step of this activity ?
                    records["prov:Entity"].append(e)
                else:
                    closest_entity = max(
                        records["prov:Entity"],
                        key=lambda a: SequenceMatcher(
                            None, a["label"], entity_name
                        ).ratio(),
                    )
                    a["used"].append(closest_entity["@id"])
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
