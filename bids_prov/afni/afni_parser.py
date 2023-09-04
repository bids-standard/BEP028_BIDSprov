import argparse
import copy
import json
import os
import re
from collections import defaultdict, OrderedDict
from itertools import chain

from bids_prov.fsl.fsl_parser import get_entities
from bids_prov.utils import get_default_graph, CONTEXT_URL, get_id, label_mapping, compute_sha_256_entity, \
    writing_jsonld

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


def find_param(cmd_args_remain: list) -> dict:
    """ Find parameter in all command arguments that remain after entities extraction

    Parameters
    ----------
    cmd_args_remain : list of str
        all arguments that have not been used for extracting input/output entities

    Returns
    -------
    dict :
        [key:value} where key is parameter name and value is True if no value is given in command arguments,
        else its value
    """
    param_dic = {}
    for arg_remain in cmd_args_remain:
        if arg_remain.startswith("-"):
            if arg_remain != cmd_args_remain[-1]:
                succesor = cmd_args_remain[cmd_args_remain.index(arg_remain) + 1]
                if not succesor.startswith("-"):
                    param_dic[arg_remain] = succesor
                    cmd_args_remain.remove(succesor)
                else:
                    param_dic[arg_remain] = True
            else:
                param_dic[arg_remain] = True

    return param_dic


def build_records(commands_bloc: list, agent_id: str, verbose: bool = False):
    """
    Build the `records` field for the final .jsonld file,
    from commands lines grouped by stage (e.g. `Registration`, `Post-stats`)

    Parameters
    ----------

    commands_bloc : list of str
        all commands extracted from afni file
    agent_id : int
        random uuid for software agent (here afni)
     verbose : bool, default=False
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

    bloc_act = []

    for (bloc, cmd) in commands_bloc:
        cmd_s = re.split(" |=", cmd)
        a_name = cmd_s[0]
        cmd_args_remain = cmd_s[1:]
        inputs = []
        outputs = []
        function_in_description_functions = False
        command_name_end = os.path.split(a_name)[1]

        for df in description_functions:
            if df["Name"] == command_name_end:
                function_in_description_functions = True

                inputs, outputs, cmd_args_remain = get_entities(cmd_s[1:], df)

                # if "Used" in df:
                #     arg = df["Used"]
                #     entities, args_consumed_list = get_entities(cmd_s, arg)
                #     renamed_entities = [clean_label_suffix(
                #         os.path.split(ent)[1]) for ent in entities]
                #     inputs.extend(renamed_entities)
                #     for arg in args_consumed_list:
                #         cmd_args_remain.remove(arg)

                # if "GeneratedBy" in df:
                #     arg = df["GeneratedBy"]
                #     entities, args_consumed_list = get_entities(cmd_s, arg)
                #     renamed_entities = [clean_label_suffix(
                #         os.path.split(ent)[1]) for ent in entities]
                #     outputs.extend(renamed_entities)
                #     for arg in args_consumed_list:
                #         cmd_args_remain.remove(arg)

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
            "Label": label_mapping(label, "afni/afni_labels.json"),
            "AssociatedWith": "urn:" + agent_id,
            "Command": cmd,
            "Parameters": param_dic,
            "Used": list(),
        }

        for input_path in inputs:
            input_id = f"urn:{get_id()}"  # def format_id
            existing_input = next(
                (entity for entity in records["Entities"] if entity["AtLocation"] == input_path), None)

            if existing_input is None:
                new_label = os.path.split(input_path)[1]
                new_label_rename = clean_label_suffix(new_label)
                ent = {
                    "@id": input_id,
                    "Label": new_label_rename,
                    "AtLocation": input_path,
                }
                records["Entities"].append(ent)
                activity["Used"].append(input_id)
            else:
                activity["Used"].append(existing_input["@id"])

        for output_path in outputs:
            records["Entities"].append(
                {
                    "@id": f"urn:{get_id()}",
                    "Label": os.path.split(output_path)[1],
                    "AtLocation": output_path,
                    "GeneratedBy": activity["@id"],
                    # "derivedFrom": input_id,
                }
            )
        bloc_act.append((bloc, activity["@id"]))

        records["Activities"].append(activity)
        if verbose:
            print('-------------------------')

    return dict(records), bloc_act


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

    # commands = [cmd for cmd in commands if not any(
    #     cmd.startswith(begin) for begin in dropline_begin)]
    regex_bloc = re.compile(r'# =+ ([^=]+) =+')
    commands_bloc = []
    bloc = ""
    for cmd in commands:
        if cmd.startswith("# ==="):
            bloc = regex_bloc.match(cmd).groups()[0] if regex_bloc.match(cmd) is not None else "bloc ..."

        if not any(cmd.startswith(begin) for begin in dropline_begin):
            commands_bloc.append((bloc, cmd))

    commands_bloc = [(bloc, re.sub(r"\s+", " ", cmd))
                     for (bloc, cmd) in commands_bloc]  # drop multiple space between args

    commands_bloc = [(bloc, cmd)
                     for (bloc, cmd) in commands_bloc if cmd]  # drop empty commands

    return commands_bloc


def get_activities_by_ids(graph, ids):
    """
    Get activities from graph by ids

    Parameters
    ----------
    graph : dict
        The bids-prov graph

    ids : list
        list of int that are id of activities 

    Returns
    -------
    activities : list 
        list of activities 
    """
    activities = []
    for activity in graph["Records"]["Activities"]:
        if activity["@id"] in ids:
            activities.append(activity)
    return activities


def fusion_activities(activities, label):
    """
    Fusion in a single activity the activities

    Parameters
    ----------
    activities : list 
        list of activities 

    label : string
        name of the group

    Returns
    -------
    activities : fict 
        The final activity 
    """
    if len(activities) > 0:
        used_entities = []
        command = ""

        for activity in activities:
            used_entities.extend(activity["Used"])
            command += activity["Command"] + "; "

        return {
            "@id": f"urn:{get_id()}",
            "Label": label,
            "AssociatedWith": activities[0]["AssociatedWith"],
            "Command": command,
            "Used": used_entities,
        }


def get_extern_entities_from_activities(graph, activities, id_fusion_activity):
    """
    Get the extern entities from activities

    Parameters
    ----------
    graph : dict
        The bids-prov graph

    activities : list 
        list of activities 

    id_fusion_activity : int
        id of the final activity

    Returns
    -------
    activities : list 
        List extern entities
    """
    if len(activities) > 0:
        activities_ids = [act["@id"] for act in activities]
        used_ents_ids = []
        for act in activities:
            used_ents_ids.extend(act["Used"])
        used_ents_ids = set(used_ents_ids)

        used_ents = []
        generated_entities = []
        for ent in graph["Records"]["Entities"]:
            if ent["@id"] in used_ents_ids:
                if "GeneratedBy" in ent:
                    if ent["GeneratedBy"] not in activities_ids:
                        used_ents.append(ent)
                else:
                    used_ents.append(ent)

            if "GeneratedBy" in ent:
                if ent["GeneratedBy"] in activities_ids:
                    if ent["@id"] not in used_ents_ids:
                        generated_entities.append(ent)

        # for ent in used_ents:
        #     if "GeneratedBy" in ent:
        #         ent["GeneratedBy"] = id_fusion_activity

        for ent in generated_entities:
            if "GeneratedBy" in ent:
                ent["GeneratedBy"] = id_fusion_activity

        return used_ents + generated_entities


def afni_to_bids_prov(filename: str, context_url=CONTEXT_URL, output_file=None,
                      soft_ver='afni24', indent=2, verbose=True, with_blocs=True) -> bool:
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
    indent : int
        number of indentation in jsonld
    verbose : bool
        True to have more verbosity
    with_blocs : bool
        To retrieve or not the results of the parser in block mode and not only for each command

    Returns
    -------
    bool
        Write the json-ld to the location indicated in output_file.
        If `with_blocs` is True, it generates the file to the location indicated in output_file.
    """
    commands_bloc = readlines(filename)

    graph, agent_id = get_default_graph(label="AFNI", context_url=context_url, soft_ver=soft_ver)
    records, bloc_act = build_records(commands_bloc, agent_id, verbose=verbose)

    graph["Records"].update(records)
    compute_sha_256_entity(graph["Records"]["Entities"])

    if with_blocs:
        bl_name = list(OrderedDict.fromkeys(bl for (bl, id) in bloc_act))
        blocs = [{
            "bloc_name": bl,
            "act_ids": [id_ for (b, id_) in bloc_act if b == bl]} for bl in bl_name]

        graph_bloc = copy.deepcopy(graph)
        activities_blocs = []
        entities_blocs = []
        for bloc in blocs:
            activities = get_activities_by_ids(graph_bloc, bloc["act_ids"])
            fus_activities = fusion_activities(activities, bloc["bloc_name"])
            ext_entities = get_extern_entities_from_activities(
                graph_bloc, activities, fus_activities["@id"])
            for ent in ext_entities:
                if ent["@id"] not in entities_blocs:
                    entities_blocs.append(ent)

            for ent_used in fus_activities["Used"]:
                if ent_used not in [id_["@id"] for id_ in ext_entities]:
                    fus_activities["Used"].remove(ent_used)
            activities_blocs.append(fus_activities)

        graph_bloc["Records"]["Activities"] = activities_blocs
        graph_bloc["Records"]["Entities"] = entities_blocs

        return writing_jsonld(graph_bloc, indent, output_file)

    return writing_jsonld(graph, indent, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="./examples/from_parsers/afni/afni_default_proc.sub_001",
                        help="afni execution log file")
    parser.add_argument("--output_file", type=str, default="res.jsonld", help="output dir where results are written")
    parser.add_argument("--context_url", default=CONTEXT_URL, help="CONTEXT_URL")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    afni_to_bids_prov(opt.input_file, context_url=opt.context_url, output_file=opt.output_file, verbose=opt.verbose)
    # > python -m   bids_prov.afni.afni_parser --input_file ./afni_test_local/afni_default_proc.sub_001  --output_file res.jsonld
