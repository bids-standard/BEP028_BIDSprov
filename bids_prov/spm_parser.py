import sys
import click
import json
import re

from collections import defaultdict

import random
import string

get_id = lambda: "".join(random.choice(string.ascii_letters) for i in range(10))


def realines(filename):
    with open(filename) as fd:
        for line in fd:
            if line.startswith("matlabbatch"):
                yield line[:-1]  # remove "\n"


def group_lines(lines):
    res = defaultdict(list)
    key = lambda line: re.finditer(r"\{\d+\}", line)
    for line in lines:
        a = next(re.finditer(r"\{\d+\}", line), None)
        b = line.split(".")[2]
        if a and b:
            g = a.group()
            k = (b, g)
            res[k].append(line[len(f"matlabbatch{g}.") :])

    return dict(res)


def get_records(task_groups, records=defaultdict(list)):
    entities_ids = set()
    for _, values in task_groups.items():
        activity_name = "".join(_)
        activity_id = "niiri:" + activity_name + get_id()
        activity = {
            "@id": activity_id,
            "label": "".join(activity_name),
        }
        # TODO : add time to activity
        # import pdb; pdb.set_trace()
        used = list()
        entities = []
        for v in values:
            entity_split = v.split(" = ")
            if len(entity_split) == 2:
                left, right = entity_split
                entity_label = left.split("/")[-1].split(".")[0]
                entity = {
                    "@id": "niiri:" + entity_label + get_id(),
                    "label": entity_label,
                    "prov:atLocation": right[2:-3],
                    "wasGeneratedBy": activity_id,
                }

                entities.append(entity)

        activity["used"] = [e["@id"] for e in entities]
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

    lines = realines(filename)
    tasks = group_lines(lines)
    records = get_records(tasks)
    graph["records"].update(records)

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=2)


if __name__ == "__main__":
    sys.exit(spm_to_bids_prov())
