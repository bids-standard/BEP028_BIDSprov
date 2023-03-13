import re
from collections import defaultdict
from itertools import chain
import json
import os
from typing import List, Mapping
from bs4 import BeautifulSoup
import argparse

from bids_prov.utils import get_default_graph, CONTEXT_URL, get_id, label_mapping

# regex to catch inputs
# in `cp /fsl/5.0/doc/fsl.css .files no_ext 5.0` --> only `.files` should match
# INPUT_RE:
# ([\/\w\.\?-]{3,} : match at least 3 times tokens included in this list [`/`, `\w`, `.`, `?`, `-`]
# \.? : match the character `.` between zero and once
# [\w]{2,} : match at least 2 times a word character
INPUT_RE = r"([\/\w\.\?-]{3,}\.?[\w]{2,})"

# ATTRIBUTE_RE : (-+[a-zA-Z_]+) : match `-` between one and unlimited times and match between one and unlimited times
# a character in this list : [`A-Za-z`, `_`] [\s|=]? : match between 0 and 1 time a character included in this list [
# `\s`, `|`, `=`]
# ([\/a-zA-Z._\d]+)? :  match between one and unlimited times a character included in this list
# [`/`, `a-zA-Z`, `.`, `_`, `\d`(digit)]
ATTRIBUTE_RE = r"\s(-+[a-zA-Z_-]+)[\s|=]+([^\s]+)?"

# tags used to detect inputs from command lines
# eg. `/usr/share/fsl/5.0/bin/film_gls --in=filtered_func_data`
INPUT_TAGS = frozenset(
    [
        "-in",
        "-i",
        "[INPUT_FILE]",  # specific to bet2
        "-r",  # `cp -r` --> recursive ??? also used in featreg in a different context
    ]
)

# tags used to detect outputs from cammand lines
# eg. convert_xfm -inverse -omat highres2example_func.mat example_func2highres.mat
OUTPUT_TAGS = frozenset(
    [
        "-o",
        "-omat",
    ]
)


def readlines(filename: str) -> Mapping[str, List[str]]:
    """read an HTML file containing command lines

    Example
    -------
    with a file containing
    ```html
    <HTML><HEAD>
    <!--refreshstart-->

    <!--refreshstop-->
    <link REL=stylesheet TYPE=text/css href=.files/fsl.css>
    <TITLE>FSL</TITLE></HEAD><BODY><OBJECT data=report.html></OBJECT>
    <h2>Progress Report / Log</h2>
    Started at Wed  7 Mar 13:35:14 GMT 2018<p>
    Feat main script<br><pre>

    /bin/cp /tmp/feat_oJmMLg.fsf design.fsf

    /usr/share/fsl-5.0/bin/feat_model design

    mkdir .files;cp /usr/share/fsl-5.0/doc/fsl.css .files
    </pre></BODY></HTML>
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
    # Read the HTML report_log file
    with open(filename, "r") as file:
        html_code = file.read()

    # Split the HTML code into lines
    html_code_splitted = html_code.splitlines()
    # BeautifulSoup object to parse the HTML code more easily
    soup = BeautifulSoup(html_code, 'html.parser')
    # Find all pre tags in the HTML code
    pre_tags = soup.find_all('pre')

    result = {}
    for tag in pre_tags:
        # Extract the section name from the line where pre tag appeared and remove html tags
        section = re.sub("<.*?>", "", html_code_splitted[tag.sourceline - 1])
        # Get the text content within the pre tag and split it into lines
        tag_text = tag.text.splitlines()
        commands = []
        for i, line in enumerate(tag_text):
            if re.match(r"^[a-z/].*$", line) and not line.startswith("did") and tag_text[i - 1] == "":
                # the line must begin with a lowercase word or a / followed by 0 or more dots
                # and the line must be after a newline
                # rstrip remove the `\n`, split
                commands.extend(function.strip()
                                for function in line.split(";"))
                # on a possible `;` and add to the end of the list
            else:
                pass
        result[section] = commands

    return result


# def get_closest_config(key):
#     """
#     get the FSL config from bosh if possible, trying to match names
#     of executables returned from bosh with subparts of `key`
#
#     Example
#     -------
#     ```python
#     >>> stats_conf = get_closest_config("fslstats")
#     >>> stats_conf["version"]
#     5.0.9
#     ```
#     """
#     key = re.sub("\d", "", key)
#     if not key:
#         return None
#     key = next(
#         (k for k in conf.bosh_config.keys() if (k.casefold() in key.casefold() or key.casefold() in k.casefold())),
#         None)
#     if key is not None:
#         return conf.bosh_config[key]
#     return None


def get_entities(cmd_s, parameters):
    """
    Given a list of command arguments `cmd_s` and a list of `parameters`, this function returns the entities associated
    with the parameters.

    Parameters
    ----------

    cmd_s : list of str
        A list of command arguments.
    parameters : list
        A list of parameters to search for in `cmd_s`. Each parameter can either be an integer or a string. If the parameter is an integer,
    the entity will be the string in `cmd_s` at that index. If the parameter is a string, the entity will be the next
    argument in `cmd_s` after the parameter. If the parameter is a dict, the entity (or entities) will be obtained
    with the position of the argument and an offset index

    Returns
    -------
    list of str A list of entities associated
    with the parameters.

    Example
    -------
    >>> cmd_s = ["command", "-a", "input1", "-b", "input2"]
    >>> parameters = [2, 4, "-a"]
    >>> get_entities(cmd_s, parameters)
    ['input1', 'input2', 'input1']
    """
    entities = []
    args_consumed_list = []
    for u_arg in parameters:
        if type(u_arg) == int:
            if not cmd_s[u_arg].startswith("-") :
                entities.append(cmd_s[u_arg])   # the "if" is useful for
            # Entities that are optional but indicated in the description file
            # Example : "/slicer rendered_thresh_zstat2 -A 750 zstat2.png" with "used": [1, 2]
            # Sometimes, 2 is present. In the previous command, this is not the case
                args_consumed_list.append(cmd_s[u_arg])
        elif type(u_arg) == dict:
            # Allows us to retrieve entities not directly attached to the parameter name
            # Example : "/slicer rendered_thresh_zstat2 -A 750 zstat2.png" with "generatedBy":
            # [{"name": "-A", "index": 2}]
            if u_arg["name"] in cmd_s:
                entities.extend([cmd_s[i + u_arg["index"]] for i, cmd_part in enumerate(cmd_s) if cmd_part == u_arg["name"]])
                # The for loop allows to retrieve the entities of the parameters appearing several times
                # Example : /slicer example_func2highres highres -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png
        else:  # type(u_arg) == str
            if u_arg in cmd_s:
                entities.append(cmd_s[cmd_s.index(u_arg) + 1])  # we add the entity located just after the parameter
                if u_arg.startswith("-") or '>' in u_arg :
                    args_consumed_list.append(cmd_s[cmd_s.index(u_arg) + 1])
                    args_consumed_list.append(u_arg)
            elif not u_arg.startswith("-"):  # case of slicing
                u_arg_splitted = u_arg.split(":")
                start = int(u_arg_splitted[0])
                if u_arg_splitted[1] == "":
                    stop = None
                else:
                    stop = int(u_arg_splitted[-1])

                if re.search(r"(-f|-rf)", cmd_s[1]):# to skip -r or -rf option
                     add_ent = cmd_s[slice(start+1, stop)]
                else:
                    add_ent = cmd_s[slice(start, stop)]
                entities.extend(add_ent)
                args_consumed_list.extend(add_ent)

    return entities, args_consumed_list


def build_records(groups: Mapping[str, List[str]], agent_id: str):
    """
    Build the `records` field for the final .jsonld file,
    from commands lines grouped by stage (e.g. `Registration`, `Post-stats`)

    Returns
    -------
    dict: a set of records compliant with the BIDS-prov standard
    """
    records = defaultdict(list)

    filepath = os.path.join(os.path.dirname(__file__),"description_functions.json")
    with open(filepath) as f:
        description_functions = json.load(f)

    for k, v in groups.items():
        print(k, ":", v)
        if k == "Feat main script":  # skip "Feat main script" section
            continue
        # group_name = k.lower().replace(" ", "_")  # TODO

        for cmd in v:
            # process to remove + and - in pngappend command
            cmd = cmd.replace(" + ", " ").replace(" - ", " ")
            cmd_s = re.split(" |=", cmd)
            a_name = cmd_s[0]

            inputs = []
            outputs = []
            parameters = []
            entity_names = []

            function_in_description_functions = False

            command_name_end = os.path.split(a_name)[1]
            for df in description_functions:
                if df["name"] == command_name_end:
                    function_in_description_functions = True
                    if "used" in df:
                        entities, _ = get_entities(cmd_s, df["used"])
                        inputs.extend(entities)
                    if "generatedBy" in df:
                        entities, _ = get_entities(cmd_s, df["generatedBy"])
                        outputs.extend(entities)
                    # if command_name_end == "fslmaths" and "-odt" not in cmd_s:
                    #     outputs.append(cmd_s[-1])
                    break

            if function_in_description_functions is False:
                # if the function is not in our description file, the process is based on regex
                attributes = defaultdict(list)

                # same key can have multiple value
                for key, value in re.findall(ATTRIBUTE_RE, cmd):
                    attributes[key].append(value)

                # make sure attributes are not considered as entities
                cmd_without_attributes = re.sub(ATTRIBUTE_RE, "", cmd)

                # if a key of attributes is in INPUT_TAGS, we add her value in inputs
                inputs = list(chain(*(attributes.pop(k) for k in attributes.keys() & INPUT_TAGS)))
                # same process with OUTPUT_TAGS
                outputs = list(chain(*(attributes.pop(k) for k in attributes.keys() & OUTPUT_TAGS)))
                entity_names = [_ for _ in re.findall(INPUT_RE, cmd_without_attributes[len(a_name):])]

            # # cmd_conf = get_closest_config(a_name)  # with the module boutiques
            # cmd_conf = None  # None because boutiques is not used at this time
            # # if cmd_conf:
            # #     pos_args = filter(lambda e: not e.startswith("-"), cmd_s)  # TODO use "-key value" mappings
            # #     _map = dict(zip(cmd_conf["command-line"].split(" "), pos_args))
            # #     inputs += [_map[i] for i in INPUT_TAGS if i in _map]

                if entity_names and entity_names[0] in cmd_without_attributes:
                    outputs.append(entity_names[-1])
                    if len(entity_names) > 1:
                        inputs.append(entity_names[0])

            label = f"{os.path.split(a_name)[1]}" # the file name and possible extension

            a = {
                "@id": f"urn:{get_id()}",
                "label": label_mapping(label, "fsl/fsl_labels.json"),
                "associatedWith": "urn:" + agent_id,
                "command": cmd,
                # "attributes": [
                #     {k: v if len(v) > 1 else v[0]} for k, v in attributes.items()
                # ],
                "used": list(),
            }

            # input_id = ""
            for input_path in inputs:
                # input_name = input_path.replace("/", "_") # TODO
                input_id = f"urn:{get_id()}"  # def format_id

                existing_input = next(
                    (entity for entity in records["prov:Entity"] if entity["prov:atLocation"] == input_path), None)
                if existing_input is None:
                    e = {
                        "@id": input_id,
                        "label": os.path.split(input_path)[1],
                        "prov:atLocation": input_path,
                    }
                    records["prov:Entity"].append(e)
                    a["used"].append(input_id)
                else:
                    a["used"].append(existing_input["@id"])

            for output_path in outputs:
                # output_name = output_path.replace("/", "_") # TODO
                records["prov:Entity"].append(
                    {
                        "@id": f"urn:{get_id()}",
                        "label": os.path.split(output_path)[1],
                        "prov:atLocation": output_path,
                        "generatedBy": a["@id"],
                        # "derivedFrom": input_id,
                    }
                )

            records["prov:Activity"].append(a)
    return dict(records)


def fsl_to_bids_prov(filename: str, context_url=CONTEXT_URL, output_file=None,
                     soft_ver="xxx", indent=2, verbose=False) -> None:  # TODO : add fsl version

    graph, agent_id = get_default_graph(label="FSL", context_url=context_url, soft_ver=soft_ver)

    lines = readlines(filename)
    records = build_records(lines, agent_id)
    graph["records"].update(records)

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="./examples/fsl_default/report_log.html", help="fsl execution log file")
    parser.add_argument("--output_file", type=str, default="./examples/fsl_default/report_log.jsonld", help="output dir where results are written")
    parser.add_argument("--context_url", default=CONTEXT_URL, help="CONTEXT_URL")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    fsl_to_bids_prov(opt.input_file, context_url=opt.context_url, output_file=opt.output_file, verbose=opt.verbose)
    # #
    # input_file = os.path.abspath("../../examples/from_parsers/fsl/fsl_full_examples001_report_log.html")
    # output_file = "../../res.jsonld"
    # random.seed(14)
    # fsl_to_bids_prov(input_file, context_url=CONTEXT_URL, output_file=output_file, verbose=False)
