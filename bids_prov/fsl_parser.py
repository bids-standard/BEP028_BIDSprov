import click
import re
import sys
from collections import defaultdict
import requests
import json

import prov.model as prov


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


def build_document(groups: dict, ctx: dict):  # TODO
    document = prov.ProvDocument()
    # for k, v in ctx.items():
    #    if isinstance(v, str) and not k.startswith("@"):
    #        document.add_namespace(k, v)

    # document.agent(identifier="RRID:SCR_002823", other_attributes={  # FIXME ProvElementIdentifierRequired: An identifier is missing. All PROV elements require a valid identifier.
    # "@type" : "prov:SoftwareAgent",
    #    "label" : "FSL",
    # })

    for a_i, (k, v) in enumerate(groups.items()):
        a = document.activity(
            "niiri:" + str(a_i),
            other_attributes={
                # "label" : k.lower().replace(" ", ""),  # prov.model.ProvExceptionInvalidQualifiedName: Invalid Qualified Name: label
                # "wasAssociatedWith": "RRID:SCR_002823",
            },
        )
        for cmd in v:
            attributes = re.findall(r"(-[a-zA-Z][^-]*)\s([a-zA-Z\d\.]+)", cmd)
    return


def build_records(groups: dict):
    records = defaultdict(list)

    for a_i, (k, v) in enumerate(groups.items()):
        a = {
            "@id": "niiri:" + str(a_i),
            "label": k.lower().replace(" ", ""),
            "wasAssociatedWith": "RRID:SCR_002823",
            "attributes": list(),
            "used": list(),
        }
        entities = list()
        for cmd in v:
            import pdb

            pdb.set_trace()
            params = re.findall(r"-([a-zA-Z][^-]*)[\s=]+([a-zA-Z\d\.]+)", cmd)
            cmd = re.sub(
                r"-([a-zA-Z][^-]*)[\s=]+([a-zA-Z\d\.]+)", "", cmd
            )  # remove params
            entity_names = re.findall(r"(\/?[^ ]*\.[\w:]+)", cmd)
            # entity_names = [_ for _ in cmd.split(" ") if re.match(r"(/?[a-z]+)+\.[a-z]+", _)]
            for p_name, p_val in params:
                a["attributes"].append((p_name, p_val))

            for entity_name in entity_names:
                e_id = entity_name  # TODO improve
                e = {
                    "@id": "niiri:" + str(entity_name),  # TODO : uuid
                    "label": entity_name,
                    "prov:atLocation": e_id,
                    "wasAttributedTo": "RRID:SCR_002823",
                    "derivedFrom": "TODO",
                }
                if entity_name == entity_names[-1]:  # output
                    e["wasGeneratedBy"] = a[
                        "@id"
                    ]  # wasAffectedBy if enity is ther result of an intermediate step of this activity ?
                else:
                    a["used"].append(e_id)
                entities.append(e)
        records["prov:Activity"].append(a)
        records["prov:Entity"].extend(entities)
    return dict(records)


@click.command()
@click.argument("filenames", nargs=-1)
@click.option("--output-file", "-o", required=True)
@click.option(
    "--context-url",
    "-c",
    default="https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json",
)
def fsl_to_bids_pros(filenames, output_file, context_url):
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
                    "@id": "RRID:SCR_002823",  # TODO query for version
                    "@type": "prov:SoftwareAgent",
                    "label": "FSL",
                }
            ],
            "prov:Activity": [],
            "prov:Entity": [],
        },
    }

    import urllib.request, json

    with urllib.request.urlopen(context_url) as url:
        ctx = json.loads(url.read().decode()).get("@context", dict())

    lines = readlines(filename)
    records = build_records(lines)
    graph["records"].update(records)

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=2)


if __name__ == "__main__":
    sys.exit(fsl_to_bids_pros())
