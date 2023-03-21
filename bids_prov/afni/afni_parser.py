import argparse
import re
import json
import os
from collections import defaultdict
from itertools import chain

# from bids_prov.fsl.fsl_parser import get_entities
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
# e.g. `/usr/share/fsl/5.0/bin/film_gls --in=filtered_func_data`
INPUT_TAGS = frozenset(
    [
        "-in",
        "-i",
        "[INPUT_FILE]",  # specific to bet2
        "-r",  # `cp -r` --> recursive ??? also used in featreg in a different context
    ]
)

# tags used to detect outputs from command lines
# e.g. convert_xfm -inverse -omat highres2example_func.mat example_func2highres.mat
OUTPUT_TAGS = frozenset(
    [
        "-o",
        "-omat",
    ]
)


def clean_label_suffix(label: str) -> str:
    """ Erase suffix like tlrc in label to keep link of passed entities label
    """
    new_label_rename = re.sub(r"\+tlrc", "", label)
    new_label_rename = re.sub(r"\+orig", "", new_label_rename)
    new_label_rename = re.sub(r"'\[.*\]'", "", new_label_rename)
    new_label_rename = re.sub(r".HEAD", "", new_label_rename)
    new_label_rename = re.sub(r"\"\[.*\]\"", "", new_label_rename)
    new_label_rename = re.sub(r"::WARP_DATA", "", new_label_rename)
    return new_label_rename


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
            if not cmd_s[u_arg].startswith("-"):
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
                entities.extend([cmd_s[i + u_arg["index"]]
                                for i, cmd_part in enumerate(cmd_s) if cmd_part == u_arg["name"]])
                # The for loop allows to retrieve the entities of the parameters appearing several times
                # Example : /slicer example_func2highres highres -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png
        else:
            # type(u_arg) == str
            if u_arg in cmd_s:
                # we add the entity located just after the parameter
                entities.append(cmd_s[cmd_s.index(u_arg) + 1])
                if u_arg.startswith("-") or '>' in u_arg:
                    args_consumed_list.append(cmd_s[cmd_s.index(u_arg) + 1])
                    args_consumed_list.append(u_arg)
            elif not u_arg.startswith("-"):  # case of slicing
                u_arg_splitted = u_arg.split(":")
                start = int(u_arg_splitted[0])
                if u_arg_splitted[1] == "":
                    stop = None
                else:
                    stop = int(u_arg_splitted[-1])

                # to skip -r or -rf option
                if re.search(r"(-f|-rf)", cmd_s[1]):
                    add_ent = cmd_s[slice(start+1, stop)]
                else:
                    add_ent = cmd_s[slice(start, stop)]
                entities.extend(add_ent)
                for ent in add_ent:
                    args_consumed_list.append(ent)
    renamed_entities = []
    for ent in entities:
        new_label = os.path.split(ent)[1]
        new_label_rename = clean_label_suffix(new_label)
        renamed_entities.append(new_label_rename)
    # print("entities: ",entities, " renamed_entities:", renamed_entities)

    return renamed_entities, args_consumed_list


def find_param(cmd_args_remain: list) -> dict:
    """ Find parameter in all command arguments that remain after entities extraction

    Parameters
    ----------
    cmd_args_remain : list of str
        all arguments that have not been used for extracting input/output entities

    Returns
    -------
    dict :
        [key:value} where key is parameter name and value is True if no value is given in command arguments, else its value
    """
    param_dic = {}
    for arg_remain in cmd_args_remain:
        if arg_remain.startswith("-"):
            if arg_remain != cmd_args_remain[-1]:
                succesor = cmd_args_remain[cmd_args_remain.index(arg_remain)+1]
                if not succesor.startswith("-"):
                    param_dic[arg_remain] = succesor
                    cmd_args_remain.remove(succesor)
                else:
                    param_dic[arg_remain] = True
            else:
                param_dic[arg_remain] = True

    return param_dic


def build_records(commands: list, agent_id: str, verbose=False):
    """
    Build the `records` field for the final .jsonld file,
    from commands lines grouped by stage (e.g. `Registration`, `Post-stats`)

    Parameters
    ----------

    commands : list of str
        all commands extracted from afni file
    agent_id : int
        random uuid for software agent (here afni)
     verbose : bool
        True to have more verbosity

    Returns
    -------
    dict: a set of records compliant with the BIDS-prov standard
    """
    records = defaultdict(list)
    filepath = os.path.join(os.path.dirname(__file__),
                            "description_functions.json")
    with open(filepath) as f:
        description_functions = json.load(f)

    for cmd in commands:
        cmd_s = re.split(" |=", cmd)
        a_name = cmd_s[0]
        cmd_args_remain = cmd_s[1:]
        inputs = []
        outputs = []
        function_in_description_functions = False
        command_name_end = os.path.split(a_name)[1]

        for df in description_functions:
            if df["name"] == command_name_end:
                function_in_description_functions = True
                for key, ent_list in zip(["used", "generatedBy"], [inputs, outputs]):
                    if key in df:
                        entities, args_consumed_list = get_entities(
                            cmd_s, df[key])
                        renamed_entities = [clean_label_suffix(
                            os.path.split(ent)[1]) for ent in entities]
                        ent_list.extend(renamed_entities)
                        for arg in args_consumed_list:
                            cmd_args_remain.remove(arg)

                break

        param_dic = find_param(cmd_args_remain)

        if verbose:
            print("CMD", cmd)
            print('-> inputs: ', inputs)
            print('<- outputs: ', outputs)
            print("  others args :", *cmd_args_remain)
            print("Parameters :")
            for k, v in param_dic.items():
                print(f"{k} : {v}")

        # default behavior if function is not present in descriptions
        if function_in_description_functions is False:
            print(f"-> {command_name_end} : Not present in description_functions")

            # if the function is not in our description file, the process is based on regex
            attributes = defaultdict(list)

            # same key can have multiple value
            for key, value in re.findall(ATTRIBUTE_RE, cmd):
                attributes[key].append(value)

            # make sure attributes are not considered as entities
            cmd_without_attributes = re.sub(ATTRIBUTE_RE, "", cmd)

            # if a key of attributes is in INPUT_TAGS, we add her value in inputs
            inputs = list(chain(*(attributes.pop(k)
                          for k in attributes.keys() & INPUT_TAGS)))
            # same process with OUTPUT_TAGS
            outputs = list(chain(*(attributes.pop(k)
                           for k in attributes.keys() & OUTPUT_TAGS)))
            entity_names = [_ for _ in re.findall(
                INPUT_RE, cmd_without_attributes[len(a_name):])]

            if entity_names and entity_names[0] in cmd_without_attributes:
                outputs.append(entity_names[-1])
                if len(entity_names) > 1:
                    inputs.append(entity_names[0])

        # the file name and possible extension
        label = f"{os.path.split(a_name)[1]}"

        activity = {
            "@id": f"urn:{get_id()}",
            "label": label_mapping(label, "afni/afni_labels.json"),
            "associatedWith": "urn:" + agent_id,
            "command": cmd,
            "parameters": param_dic,
            "used": list(),
        }

        for input_path in inputs:
            input_id = f"urn:{get_id()}"  # def format_id
            existing_input = next(
                (entity for entity in records["prov:Entity"] if entity["prov:atLocation"] == input_path), None)

            if existing_input is None:
                new_label = os.path.split(input_path)[1]
                new_label_rename = clean_label_suffix(new_label)
                ent = {
                    "@id": input_id,
                    "label": new_label_rename,
                    "prov:atLocation": input_path,
                }
                records["prov:Entity"].append(ent)
                activity["used"].append(input_id)
            else:
                activity["used"].append(existing_input["@id"])

        for output_path in outputs:
            records["prov:Entity"].append(
                {
                    "@id": f"urn:{get_id()}",
                    "label": os.path.split(output_path)[1],
                    "prov:atLocation": output_path,
                    "generatedBy": activity["@id"],
                    # "derivedFrom": input_id,
                }
            )

        records["prov:Activity"].append(activity)
        if verbose:
            print('-------------------------')

    return dict(records)


def gather_multiline(input_file: str) -> list:
    """
    gather multiline command split by \ separator

    Parameters
    ----------
    input_file : str
        name of input afni file

    Returns
    -------
    commands : list
        all commands extracted from afni file without filtering

    """
    commands = []
    with open(input_file) as fd:
        for line in fd:
            # drop '\n' at end and drop blank space
            command_ = line[:-1].strip()
            if command_:  # drop blank line
                while command_.endswith('\\'):
                    command_ = command_[:-1].strip() + ' ' + \
                        next(fd)[:-1].strip()
                commands.append(command_)

    return commands


def readlines(input_file: str) -> list:
    """
    gather multiline command split by \ separator

    Parameters
    ----------
    input_file : str
        name of input afni file

    Returns
    -------
      commands : list
         all commands extracted from afni file with  filtering function that gives no input/output
    """
    commands = gather_multiline(input_file)
    filtered = "\n".join(commands)
    # drop infile text creation
    filtered = re.sub(r"cat <<EOF[\s\S]*?EOF", "", filtered)
    commands = filtered.split("\n")
    dropline_begin = ["#", "cd", "printf", "\\rm", "$cmd", 'touch', 'sleep',
                      'afni', "echo", "set", "foreach", "end", "if", "endif", "else", "exit"]
    commands = [cmd for cmd in commands if not any(
        cmd.startswith(begin) for begin in dropline_begin)]
    commands = [re.sub(r"\s+", " ", cmd)
                for cmd in commands]  # drop multiple space between args
    commands = [cmd for cmd in commands if cmd]  # drop empty commands

    return commands


def afni_to_bids_prov(filename: str, context_url=CONTEXT_URL, output_file=None,
                      soft_ver='afni24', indent=2, verbose=True) -> None:
    """
    afni parser

    Parameters
    ----------
    filename : str
        filename of  afni script
    context_url : str
        url for context bids-prov :
    output_file : str
        name of output parsed file with extension json.ld
    soft_ver:str
        version of sofware afni
    indent :int
        number of indentation in jsonld
    verbose : bool
        True to have more verbosity



    """
    commands = readlines(filename)
    graph, agent_id = get_default_graph(
        label="AFNI", context_url=context_url, soft_ver=soft_ver)
    records = build_records(commands, agent_id, verbose=verbose)
    graph["records"].update(records)
    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str,
                        default="./examples/from_parsers/afni/afni_default_proc.sub_001", help="afni execution log file")
    parser.add_argument("--output_file", type=str, default="res.jsonld",
                        help="output dir where results are written")
    parser.add_argument(
        "--context_url", default=CONTEXT_URL, help="CONTEXT_URL")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    afni_to_bids_prov(opt.input_file, context_url=opt.context_url,
                      output_file=opt.output_file, verbose=opt.verbose)
    # > python -m   bids_prov.afni.afni_parser --input_file ./afni_test_local/afni_default_proc.sub_001  --output_file res.jsonld

    # input_file = os.path.abspath("../../nidmresults-examples/narps_do_13_view_zoom.tcsh")
    # # # # # input_file = os.path.abspath("../../afni_test_local/afni/toy_afni")
    # output_file = "../../res.jsonld"
    # # commands = readlines(input_file)
    # afni_to_bids_prov(input_file, context_url = CONTEXT_URL, output_file = output_file,soft_ver = 'afni24',verbose=True)

    # Finding PREAMBULE
    # with open(input_file, "r") as file:
    #     all_lines= file.readlines()
    # all_lines = [line.strip() for line in all_lines]
    # idx_line_set_runs = all_lines.index('set runs = (`count -digits 2 1 1`)')
    # preambule, main_part = all_lines[:idx_line_set_runs+1], all_lines[idx_line_set_runs+1:]
    #
    # # print('\n'.join(preambule))
    # # print("="*50)
    # # print("END PREAMBULE")
    # # print("="*50)
    # main_part_joined ='\n'.join(main_part)
    # print('\n'.join(main_part[:45]))
    # FINDING FOREACH BLOCK with RE
    # find_foreach_block = re.findall("foreach run \(\s*\$runs\s*\)\s*([\s\S]*?)end\n", main_part_joined)
    # for_block = re.search("foreach run \(\s*\$runs\s*\)\s*([\s\S]*?)end\n", filtered)
    # print(for_block)
    # # for e in exp:
    # #     print(e)
    # for idx, match in enumerate(find_foreach_block):
    #     print("*"*60, f"\nMatch {idx}")
    #     lines = match.strip().split('\n')
    #     for line in lines:
    #         # Do something with the line
    #         print(line)
