import sys
import click
import json
import os
from difflib import SequenceMatcher

from collections import defaultdict

from .spm_config import *
from . import get_id


def format_activity_name(s, l=30):
    if s.startswith("spm."):
        s = s[4:]
    tmp = s.split(".")
    while sum(map(len, tmp)) > l:
        tmp = tmp[1:]
    return ".".join(tmp)


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

    if next(re.finditer(FILE_REGEX, right), None) is None:
        return None

    entity_label = re.sub(r"[{};\'\"]", "", right).split("/")[-1]
    entity = {
        "@id": "niiri:" + entity_label + get_id(),
        "label": entity_label,
        "prov:atLocation": right[2:-3],
        # "wasAttributedTo": "RRID:SCR_007037",
    }
    return entity


def preproc_param_value(val):
    if val[0] == "[":
        return val.replace(" ", ", ")
    return val


def get_closest_activity(records: dict, to_match: str, dep_number: str = None):
    if dep_number:
        closest_activity = next(
            filter(lambda a: a["label"].endswith(dep_number), records["prov:Activity"])
        )
    else:
        to_match = to_match.lower()  # TODO : str.lower before that
        to_match = DEPENDENCY_DICT.get(to_match, to_match)
        closest_activity = max(
            records["prov:Activity"],
            key=lambda a: SequenceMatcher(None, a["@id"], to_match).ratio(),
        )
    return closest_activity


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


def get_records(task_groups: dict, records=defaultdict(list)):
    entities_ids = set()
    for activity_name, values in task_groups.items():
        activity_id = "niiri:" + activity_name + get_id()
        activity = {
            "@id": activity_id,
            "label": format_activity_name(activity_name),
            "used": list(),
            "wasAssociatedWith": "RRID:SCR_007037",
        }
        input_entities, output_entities = list(), list()
        params = []

        for line in values:
            split = line.split(" = ")
            if len(split) != 2:
                print(f"could not parse {line}")
                continue
            left, right = split

            _in = get_input_entity(left, right)
            if _in:
                input_entities.append(_in)
            elif has_parameter(left) or has_parameter(activity_name):
                dependency = re.search(DEPENDENCY_REGEX, right, re.IGNORECASE)
                dep_number = re.search(r"{(\d+)}", right)
                if dependency is not None:
                    parts = dependency.group(1).split(": ")
                    closest_activity = get_closest_activity(
                        records,
                        to_match="".join(parts[:-1]),
                        dep_number=dep_number.group(1),
                    )
                    _id = "niiri:" + parts[-1].replace(" ", "") + get_id()
                    activity["used"].append(_id)
                    output_entities.append(
                        {
                            "@id": _id,
                            "label": parts[-1],
                            # "prov:atLocation": TODO
                            "wasGeneratedBy": closest_activity["@id"],
                            # "wasAttributedTo": "RRID:SCR_007037",
                        }
                    )
                else:
                    Warning(f"Could not parse line {line}")
            else:
                param_name = ".".join(left.split(".")[-2:])
                try:
                    param_value = preproc_param_value(right[:-1])
                    value = eval(param_value)
                    params.append([param_name, param_value])
                except:
                    continue

        if input_entities:
            activity["used"] = [e["@id"] for e in input_entities]
        entities = input_entities + output_entities
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
@click.option(
    "--context-url",
    "-c",
    default="https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json",
)
def spm_to_bids_prov(filenames, output_file, context_url):
    filename = filenames[0]  # FIXME

    graph = {
        "@context": context_url,
        "@id": "http://example.org/ds00000X",
        "generatedAt": "2020-03-10T10:00:00",
        "wasGeneratedBy": {
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
