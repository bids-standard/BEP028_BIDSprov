import re
import json
import os

from collections import defaultdict
from itertools import chain
from typing import List, Mapping

# from bids_prov.fsl import fsl_config as conf
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



def get_entities(cmd_s, parameters):
    """
    Given a list of command arguments `cmd_s` and a list of `parameters`, this function returns the entities associated
    with the parameters.

    Parameters ---------- cmd_s : list of str A list of command arguments. parameters : list A list of parameters to
    search for in `cmd_s`. Each parameter can either be an integer or a string. If the parameter is an integer,
    the entity will be the string in `cmd_s` at that index. If the parameter is a string, the entity will be the next
    argument in `cmd_s` after the parameter. If the parameter is a dict, the entity (or entities) will be obtained
    with the position of the argument and an offset index Returns ------- list of str A list of entities associated
    with the parameters.

    Example
    -------
    >>> cmd_s = ["command", "-a", "input1", "-b", "input2"]
    >>> parameters = [1, 3, "input1"]
    >>> get_entities(cmd_s, parameters)
    ['input1', 'input2', 'input1']
    """
    entities = []
    for u_arg in parameters:
        if type(u_arg) == int:
            entities.append(cmd_s[u_arg]) if not cmd_s[u_arg].startswith("-") else None  # the "if" is useful for
            # Entities that are optional but indicated in the description file
            # Example : "/slicer rendered_thresh_zstat2 -A 750 zstat2.png" with "used": [1, 2]
            # Sometimes, 2 is present. In the previous command, this is not the case
        elif type(u_arg) == dict:
            # Allows us to retrieve entities not directly attached to the parameter name
            # Example : "/slicer rendered_thresh_zstat2 -A 750 zstat2.png" with "generatedBy":
            # [{"name": "-A", "index": 2}]
            if u_arg["name"] in cmd_s:
                entities.extend([cmd_s[i + u_arg["index"]] for i, cmd_part in enumerate(cmd_s) if cmd_part == u_arg["name"]])
                # The for loop allows to retrieve the entities of the parameters appearing several times
                # Example : /slicer example_func2highres highres -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png
        else:
            # type(u_arg) == str
            if u_arg in cmd_s:
                entities.append(cmd_s[cmd_s.index(u_arg) + 1])  # we add the entity located just after the parameter
            elif not u_arg.startswith("-"):  # case of slicing
                u_arg_splitted = u_arg.split(":")
                start = int(u_arg_splitted[0])
                stop = None if u_arg_splitted[1] == "" else int(u_arg_splitted[-1])
                entities.extend(cmd_s[slice(start+1, stop)]
                                if re.search(r"(-f|-rf)", cmd_s[1])  # to skip -r or -rf option
                                else cmd_s[slice(start, stop)])
    return entities

def build_records(commands: list, agent_id: str):
    """
    Build the `records` field for the final .jsonld file,
    from commands lines grouped by stage (e.g. `Registration`, `Post-stats`)

    Returns
    -------
    dict: a set of records compliant with the BIDS-prov standard
    """
    records = defaultdict(list)

    filepath = os.path.join(os.path.dirname(__file__), "description_functions.json")
    with open(filepath) as f:
        description_functions = json.load(f)



    for cmd in commands:
        cmd = cmd.replace(" + ", " ").replace(" - ", " ")  # process to remove + and - in pngappend command
        cmd_s = re.split(" |=", cmd)
        a_name = cmd_s[0]

        inputs = []
        outputs = []
        entity_names = []

        function_in_description_functions = False

        command_name_end = os.path.split(a_name)[1]
        for df in description_functions:
            if df["name"] != command_name_end:
                continue

            function_in_description_functions = True
            if "used" in df:
                inputs.extend(get_entities(cmd_s, df["used"]))
            if "generatedBy" in df:
                outputs.extend(get_entities(cmd_s, df["generatedBy"]))
            if command_name_end == "fslmaths" and "-odt" not in cmd_s:
                outputs.append(cmd_s[-1])
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

        # cmd_conf = get_closest_config(a_name)  # with the module boutiques
        cmd_conf = None  # None because boutiques is not used at this time
        if cmd_conf:
            pos_args = filter(lambda e: not e.startswith("-"), cmd_s)  # TODO use "-key value" mappings
            _map = dict(zip(cmd_conf["command-line"].split(" "), pos_args))
            inputs += [_map[i] for i in INPUT_TAGS if i in _map]

        elif (entity_names and entity_names[
            0] in cmd_without_attributes) and function_in_description_functions is False:
            outputs.append(entity_names[-1])
            if len(entity_names) > 1:
                inputs.append(entity_names[0])

        label = f"{os.path.split(a_name)[1]}"  # the file name and possible extension

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

        input_id = ""
        for input_path in inputs:
            input_name = input_path.replace("/", "_")  # TODO
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
            output_name = output_path.replace("/", "_")  # TODO
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



def gather_multiline(input_file):
    commands = []
    with open(input_file) as fd:
        for line in fd:
            command_ = line[:-1].strip() # drop '\n' at end and drop blank space
            if command_: # drop blank line

                while command_.endswith('\\'):
                   command_ = command_[:-1].strip() + ' XXX ' + next(fd)[:-1].strip()
                commands.append(command_)

    return commands
def readlines(input_file):
    commands = gather_multiline(input_file)
    dropline_begin = ["#", 'afni', "echo", "set", "foreach", "end", "if", "endif", "else", "exit"]
    commands = [cmd for cmd in commands if not any(cmd.startswith(begin) for begin in dropline_begin)]
    return commands



if __name__ == "__main__":

    input_file = os.path.abspath("../../examples/from_parsers/afni/afni_default_proc.sub_001")
    output_file = "../../res.jsonld"
    # afni_to_bids_prov(input_file, context_url=CONTEXT_URL, output_file=output_file, verbose=False)
    with open(input_file, "r") as file:
        all_lines= file.readlines()
    all_lines = [line.strip() for line in all_lines]
    idx_line_set_runs = all_lines.index('set runs = (`count -digits 2 1 1`)')
    preambule, main_part = all_lines[:idx_line_set_runs+1], all_lines[idx_line_set_runs+1:]
    # print('\n'.join(preambule))
    # print("="*50)
    # print("END PREAMBULE")
    # print("="*50)
    main_part_joined ='\n'.join(main_part)
    # print('\n'.join(main_part[:45]))
    # find_foreach_block = re.findall("foreach run \(\s*\$runs\s*\)\s*([\s\S]*?)end\n", main_part_joined)
    # # for e in exp:
    # #     print(e)
    # for idx, match in enumerate(find_foreach_block):
    #     print("*"*60, f"\nMatch {idx}")
    #     lines = match.strip().split('\n')
    #     for line in lines:
    #         # Do something with the line
    #         print(line)


    commands = readlines(input_file)
    filtered = "\n".join(commands)
    print(filtered)
                #     # whole_line + (whole_line[i+1])
    soft_ver = 'afni24'
    graph, agent_id = get_default_graph(label="AFNI", context_url=CONTEXT_URL, soft_ver=soft_ver)
    records = build_records(commands, agent_id)
    graph["records"].update(records)
    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=2)

    # for_block = re.search("foreach run \(\s*\$runs\s*\)\s*([\s\S]*?)end\n", filtered)
    # print(for_block)