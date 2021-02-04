import sys
import click
import json
import re
import os

from collections import defaultdict

import random
import string

PATH_REGEX = r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
PARAM_REGEX = r"[^\.]+\(\d+\)"
FILE_REGEX = r"(\.[a-z]{1,3}){1,2}"

get_id = lambda: "".join(random.choice(string.ascii_letters) for i in range(10))
has_parameter = lambda line: next(re.finditer(PARAM_REGEX, line), None) is not None
# has_entity = lambda line: not has_parameter(line) and next(re.finditer(PATH_REGEX, line), None) is not None


def get_input_entity(left, right):
    """get input Entity if possible else return None

    left: string
        left side of ' = '
    right: string
        right side of ' = '
    """
    if has_parameter(left):
        return None
    if not next(re.finditer(PATH_REGEX, right), None):
        return None

    f = next(re.finditer(FILE_REGEX, right), None)
    if f is None:
        return None
    entity_label = left.split("/")[-1].split(".")[0]
    entity = {
        "@id": "niiri:" + entity_label + get_id(),
        "label": entity_label,
        "prov:atLocation": right[2:-3],
        "attributedTo": "RRID:SCR_0070037",
    }
    return entity


def preproc_param_value(val):
    if val[0] == "[":
        return val.replace(" ", ", ")
    return val


def readlines(filename):
    with open(filename) as fd:
        for line in fd:
            if line.startswith("matlabbatch"):
                yield line[:-1]  # remove "\n"


def group_lines(lines):
    res = defaultdict(list)
    for line in lines:
        a = next(re.finditer(r"\{\d+\}", line), None)
        if a:
            g = a.group()[1:-1]
            res[g].append(line[len(f"matlabbatch{g}.") + 2 :])

    new_res = dict()
    for k, v in res.items():
        common_prefix = os.path.commonprefix([_.split(" = ")[0] for _ in v])
        new_key = f"{common_prefix}_{k}"
        new_res[new_key] = [_[len(common_prefix) :] for _ in v]
    return new_res


def get_records(task_groups, records=defaultdict(list)):
    entities_ids = set()
    for activity_name, values in task_groups.items():
        activity_id = "niiri:" + activity_name + get_id()
        activity = {
            "@id": activity_id,
            "label": "".join(activity_name),
        }
        # TODO : add time to activity
        # import pdb; pdb.set_trace()
        used = list()
        entities = []
        params = []
        for line in values:
            split = line.split(" = ")
            if len(split) != 2:
                print(f"could not parse {line}")
                continue
            left, right = split

            entity = get_input_entity(left, right)
            if entity:
                entities.append(entity)
            elif has_parameter(line):
                pass
            else:
                param_name = ".".join(left.split(".")[-2:])
                try:
                    param_value = preproc_param_value(right[:-1])
                    value = eval(param_value)
                    params.append([param_name, param_value])
                except:
                    continue

        if entities:
            activity["used"] = [e["@id"] for e in entities]
        if params:
            activity["attributes"] = params
        records["prov:Activity"].append(activity)
        for e in entities:
            if e["@id"] not in entities_ids:
                records["prov:Entity"].append(e)
            entities_ids.add(e["@id"])

    return records


@click.command()
@click.argument("filenames", nargs=-1)
@click.option("--output-file", "-o", required=True)
def spm_to_bids_prov(filenames, output_file):
    filename = filenames[0]  # FIXME

    graph = {
        "@context": "https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json",
        "@id": "http://example.org/ds00000X",
        "generatedAt": "2020-03-10T10:00:00",
        "wasGeneratedBy": {  # TODO : change this
            "@id": "INRIA",
            "@type": "Project",
            "startedAt": "2016-09-01T10:00:00",
            "wasAssociatedWith": {
                "@id": "NIH",
                "@type": "Organization",
                "hadRole": "Funding",
            },
        },
        "records": {
            "prov:Agent": [
                {
                    "@id": "RRID:SCR_007037",  # TODO query for version
                    "@type": "prov:SoftwareAgent",
                    "label": "SPM",
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }

    lines = readlines(filename)
    tasks = group_lines(lines)
    records = get_records(tasks)
    graph["records"].update(records)

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=2)


if __name__ == "__main__":
    sys.exit(spm_to_bids_prov())
