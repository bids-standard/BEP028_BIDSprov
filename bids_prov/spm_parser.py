import argparse
import json
import os
import re

from collections import defaultdict
from bids_prov import spm_load_config as conf
from bids_prov import get_id
def format_activity_name(activity_name: str, l_max=30) -> str:
    """Function to get name of activity

    Parameters
    ----------
    activity_name : name of activity
    l_max : maximal length with cuts in words between dots


    Examples
    --------
    >>> print(format_activity_name("cfg_basicio.file_dir.file_ops.file_move._1"))
    file_dir.file_ops.file_move._1

    """
    # s example : cfg_basicio.file_dir.file_ops.file_move._1
    if activity_name.startswith("spm."):
        activity_name = activity_name[4:]
    act_split = activity_name.split(".")  # ['cfg_basicio', 'file_dir', 'file_ops', 'file_move', '_1']
    while sum(map(len, act_split)) > l_max:  # sum of the lengths of each element of tmp
        act_split = act_split[1:]
    return ".".join(act_split)  # file_dir.file_ops.file_move._1


def get_input_entity(right: str, verbose=False) ->  list:
    """Get input Entity if possible else return None

    # called if left has no parameter AND  right match with conf.PATH_REGEX and with conf.FILE_REGEX, example :
    'matlabbatch{4}.spm.stats.fmri_spec.sess.multi = {'/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/PREPROCESSING/ONSETS/sub-01-MultiCond.mat'};"

    Parameters
    ----------
    right : right side of ' = '
    verbose : boolean to have more verbosity
    Returns
    -------
     dict[str, str]
        else with key "@id", "label", "prov"

    """

    drop_brace = re.sub(r"[{};]", "", right)  # removes "{'" at the beginning and "'};" at the end
    file_list = drop_brace.split("',") # split if multiple files
    entities = list()

    for file_str in file_list:
        if not file_str == "":
            file_drop_quotes = re.sub(r"\'", "", file_str)  # 'ds000052/RESULTS/Sub01/con_0001.nii,1'
            file_location= re.sub(r"\,1", "", file_drop_quotes) # ds000052/RESULTS/Sub01/con_0001.nii
            entity_label_short = "_".join(file_location.split("/")[-2:]) # Sub01_con_0001.nii
            entity = {
                "@id": "niiri:" + entity_label_short + get_id(),
                "label": entity_label_short,
                "prov:atLocation": file_location
            }
            if os.path.exists(file_location):
                sha256_value = conf.get_sha256(file_location)
                checksum_name = "sha256_"+ entity["@id"]
                entity['digest'] = {checksum_name: sha256_value}

            entities.append(entity)

    return entities


def readlines(filename: str):  # -> Generator  from https://docs.python.org/3/library/typing.html
    """Read lines from the original batch.m file. A multiline matlabbatch instructions should be associated
    with a single line in the output

    Parameters
    ----------
    filename : filename of a matlab batch.m

    """
    with open(filename) as fd:
        for line in fd:
            if line.startswith("matlabbatch"):
                _line = line[:-1]  # remove "\n"
                brace_with_multiline = False
                while _line.count("{") != _line.count("}"):
                    brace_with_multiline = True
                    _line += next(fd)[:-1].lstrip() + ","  #
                if brace_with_multiline:
                    _line = _line[:-1] #drop last in case of multiline,
                while _line.count("[") != _line.count("]"):  # case of multiline for 1 instruction  matlabbatch
                    _line = _line.strip() + " " + next(fd)[:-1].lstrip()  # append
                yield _line


def group_lines(lines: list) -> dict:
    """Group line by their activity id.  The activity id is between curly brackets, for every line

    Parameters
    ----------
    lines: iterable[str]
        lines to be grouped, where every element is a python string

    Returns
    -------
    dict[int, str]
        a mapping from activity id to lines belonging to this activity
    Example
    -------
    >>> from bids_prov.spm_parser import group_lines
    >>> lines = ["batch{1}.file_ops.file_move.call", "batch{1}.file_ops.file_move.different.call"]
    >>> group_lines(lines)
    {'file_ops.file_move._1': ['call', 'different.call']}
    """
    res = defaultdict(list)  # KEYS : activity number (act_id), VALUES : rest of the line without matlabbatch{3}.
    # example: in batch_covariate.m of spm12:
    # matlabbatch{3}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
    # matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'mr vs plain covariate';
    # matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = 1;
    # matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';

    for line in lines:
        a = re.search(r"\{\d+\}", line)
        if a:
            g = a.group()[1:-1]  # retrieves the batch number without the braces , here '3'
            res[g].append(line[a.end() + 1:])
            # retrieves the rest of the line without the dot after the brace of the activity number

    # res = {..., '3', "spm.stats.con.consess{1}.tcon.name = 'mr vs plain covariate';", ...}
    new_res = dict()  # keys : common prefix shared by the functions of an activity, values : rest of each line
    for act_id, right_part_act_id_list in res.items():
        left_egal_list = [right_part_act_id.split(" = ")[0] for right_part_act_id in right_part_act_id_list]
        common_prefix = os.path.commonprefix(left_egal_list)
        after_common_list = [right_part_act_id[len(common_prefix):] for right_part_act_id in right_part_act_id_list]
        new_key = f"{common_prefix}_{act_id}"  # add to the common prefix the activity number
        new_res[new_key] = after_common_list  # keep the rest of the line
    # newres = {..., 'spm.stats.con._3':["spmmat(1) = cfg_dep('Model estimation: SP...;",
    #                                    "consess{1}.tcon.name = 'mr vs plain covariate';"
    #                                    ...], ...}
    return new_res


def get_entities_from_ext_config(conf_dic :dict, activity_name: str, activity_id: str) -> list:
    """ Get entities from external conf_dic (import yaml file)

    Parameters
    ----------
    conf_dic : configuration dict (import yaml file from call)
    activity_name : current activity name
    activity_id : current activity id

    Returns
    -------
    list[dict]
        each element is an entity dict with key    "@id", "label", "prov:atLocation", "wasGeneratedBy"
    """
    # checks if spatial.preproc is contained in the name of the current activity and if so returns spatial.preproc
    #
    # REMI like :conf_outputs = next((k for k in conf_dic if k in activity_n), None)
    # if conf_outputs is not None:
    # activity_name = conf_outputs["name"]
    # conf_outputs = conf_dic[conf_outputs]
    output_entities = list()
    for activity in conf_dic.keys():
        if activity in activity_name:
            for output in conf_dic[activity]['outputs']: #{'name': 'segment', 'outputs': ['c1xxx.nii.gz','c2xxx.nii.gz']}
                name = conf_dic[activity]['name']
                # print(f"    OOOO output {output} name {name}")
                entity = {"@id": name + '_'+  output + get_id(),
                     "label": name, # TODO
                     "prov:atLocation": output,
                     "wasGeneratedBy": activity_id,
                     }
                output_entities.append(entity)
            break  # stop for loop at first math in if statement (match activity in conf_dic)

    return output_entities  # empty list [] if no match,

def dependency_process(records_activities: list, activity: dict, right: str, verbose=False) -> dict:
    """Function to search dependent activity in right line. If found, find the corresponding activity
    in records_activities, update id in activity["used"], and return output_entity

    Parameters
    ----------
    records_activities : list of the previous recorded activities
    activity :  current activity
    right : current right end of line
    verbose : True to have more verbosity

    Returns
    -------
    output_entity : it is the generated entity with the  corresponding closest activity

    """

    dependency = re.search(conf.DEPENDENCY_REGEX, right, re.IGNORECASE)  # cfg_dep\(['"]([^'"]*)['"]\,.*
    # check if the line call cfg_dep and retrieve the first parameter retrieve all digits between parenthesis
    output_entity = dict()
    dep_number = re.search(r"{(\d+)}", right) #and retrieve the first parameter,  all digits between parenthesis
    parts = dependency.group(1).split(": ")  # retrieve name of the output_entity
    # if right = "cfg_dep('Move/Delete Files: Moved/Copied Files', substruct('.',...));"
    # return : ['Move/Delete Files', 'Moved/Copied Files'
    for act in records_activities:

        if act["label"].endswith(dep_number.group(1)):
            closest_activity = act
            if verbose:
                print(f"closest_activity : {closest_activity}")
            output_id = ("niiri:" + parts[-1].replace(" ", "") + dep_number.group(1))  # example : "niiri:oved/CopiedFiles1

            activity["used"].append(output_id)  # adds to the current activity the fact that it has used the previous entity
            output_entity = {"@id": output_id,
                             "label": parts[-1],
                             # "prov:atLocation": TODO
                             "wasGeneratedBy": closest_activity["@id"],
            }


    return output_entity

def get_records(task_groups: dict, verbose=False) -> dict:
    """Take the result of `group_lines` and output the corresponding  JSON-ld graph as a python dict

    Parameters
    ----------
    task_groups : task activities grouped by activity number
    verbose : True to have more verbosity

    Returns
    -------
    dict[str, list]
        records : dict with key "@context", ... "records":{"prov:Agent": ..."prov:Activity":..."prov:Entity":....}

    """

    records = defaultdict(list)
    entities_ids = set()

    for common_prefix_act, end_line_list in task_groups.items():

        activity_id = "niiri:" + common_prefix_act + get_id() # TODO enlever le common prefix
        activity = {"@id": activity_id,
                    "label": format_activity_name(common_prefix_act),
                    "used": list(),
                    "wasAssociatedWith": "RRID:SCR_007037",  # TODO ?
        }

        output_entities, input_entities = list(), list()
        params = {}

        output_ext_entity = get_entities_from_ext_config(conf.static["activities"], common_prefix_act, activity_id)
        output_entities.extend(output_ext_entity)

        for end_line in end_line_list:

            split = end_line.split(" = ")  # split in 2 at the level of the equal the rest of the action
            if len(split) != 2:
                print(f"could not parse with more than 2 '=' in end line : ' {end_line}'") # TODO not cover by test
                continue  # skip end of loop for end_line in end_line_list:

            left, right = split

            if verbose:
                print(f'MATLAB common_prefix_act: {common_prefix_act}: left: ', left, '= right: ', right)


            if not conf.has_parameter(left) and re.search(conf.PATH_REGEX, right) and re.search(conf.FILE_REGEX, right):
                # left has no parameter AND  right match with conf.PATH_REGEX and with conf.FILE_REGEX
                in_entity = get_input_entity(right, verbose=verbose)
                input_entities.extend(in_entity)
                if verbose:
                    print('-> input  entity: ', in_entity)

            elif (conf.has_parameter(left) or conf.has_parameter(common_prefix_act)) \
                    and any(["substruct" in l for l in [common_prefix_act, left, right]]):
                dependency = re.search(conf.DEPENDENCY_REGEX, right, re.IGNORECASE)  # cfg_dep\(['"]([^'"]*)['"]\,.*
                # check if the line call cfg_dep
                # or has_parameter(common_prefix_act) is mandatory because if in our activity we have only one call
                # to a function, the common part will be full and so left will be empty

                if dependency is not None:
                    output_entity = dependency_process(records["prov:Activity"],  activity, right, verbose=False)
                    output_entities.append(output_entity)
                    if verbose:
                        print('-> output  entity: ', output_entity)

                else:  # dependency is None no r"(d+)" # TODO not cover by test
                    Warning(f"Could not parse line with dependency {right}")
                    continue # break to for common_prefix_act,

            else:  # Not if in_entity and Not   (conf.has_parameter(left) ....)

                # param_name = ".".join(left.split(".")[-2:])  # split left by "." and keep the two last elements
                param_name = left.strip()
                right_= right[:-1]  # remove ";" at the end of right
                param_value = right_ if not right_.startswith("[") else right_.replace(" ", ", ")
                params[param_name] = param_value # example : [4 2] becomes [4, 2]
                if verbose:
                    print(f"param_name: {param_name}, param_value: {param_value}")
                # HANDLE STRUCTS eg. struct('name', {}, 'onset', {}, 'duration', {})
                # if param_value.startswith("struct"):
                #     continue  # TODO handle dictionary-like parameters
                # try:
                #     eval(param_value)  # Convert '5' to 5
                #     # print(f"ok {param_value}")
                #
                # except:
                #     print(f"PARAM value except {param_value}  \n")
                #     Warning(f"could not set {param_name} to {param_value}")
                #     # "struct('name', {}, 'levels', {})" dans batch_example_spm
                #     # Inf dans spm_HRF_informed_basis
                #     # DONE spm_non_sphericity
                #     #  if right {'/storage/essicdULTS/Sub01/CanonicalHRF/con_0001.nii,1', ........};,
                #     #  param_value still have an extra ;
                #
                ## params.append([param_name, param_value])
                # finally:


        if input_entities:
            used_entities = [entity["@id"] for entity in input_entities]
            activity["used"] = (activity["used"] + used_entities)  # we add entities from input_entities
            if verbose:
                print(f'activity["used"] : {activity["used"]}')

        entities = input_entities + output_entities

        if params:
            activity["parameters"] = params

        records["prov:Activity"].append(activity)

        for entity in entities:
            if entity["@id"] not in entities_ids:
                records["prov:Entity"].append(entity)
            entities_ids.add(entity["@id"])

    return records

def spm_to_bids_prov(filename: str, context_url=conf.CONTEXT_URL, output_file=None, spm_ver="SPM12r7224", verbose=False, indent=2) -> None:
    """ Exporter from batch.m to an output jsonld

    Parameters
    ----------
    filename : str
        input file of batch.m; example filename = "/test/spm_batch.m"
    context_url : str, optional
        url of context, by default conf.CONTEXT_URL=
    output_file : str, optional
        if None, default is filename with jsonld extension = "/test/spm_batch.jsonld"
    verbose : bool, optional
        False with less verbosity by default
    indent : int, optional
        2, number of indentation in jsonfile between each object


    """
    graph = conf.get_empty_graph(context_url=context_url, spm_ver=spm_ver)

    lines = readlines(filename)
    tasks = group_lines(lines)  # same as list(lines) to expand generator
    records = get_records(tasks, verbose=verbose)
    graph["records"].update(records)

    if output_file is None:
        output_file = os.path.splitext(filename)[0] + '.jsonld'  # replace extension .m by .jsonld

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="./examples/spm_default/batch.m",
                        help="data dir where batch.m are researched")
    parser.add_argument("--output_file", type=str, default="res.jsonld", help="output dir where results are written")
    parser.add_argument("--context_url", default=conf.CONTEXT_URL, help="CONTEXT_URL")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    spm_to_bids_prov(opt.input_file, context_url=opt.context_url, output_file=opt.output_file, verbose=opt.verbose)
     # > python -m   bids_prov.spm_parser --input_file ./nidm-examples/spm_covariate/batch.m --output_file ./res_temp.jsonld


