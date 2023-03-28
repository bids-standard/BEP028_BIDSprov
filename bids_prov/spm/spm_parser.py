import argparse
import json
import os
import re
from collections import defaultdict
from typing import List, Dict, Generator

from bids_prov.spm import spm_config as conf
from bids_prov.utils import get_id, get_default_graph, get_sha256, CONTEXT_URL, label_mapping


def format_activity_name(activity_name: str) -> str:
    """Function to get name of activity

    Parameters
    ----------
    activity_name : name of activity

    Examples
    --------
    >>> print(format_activity_name("cfg_basicio.file_dir.file_ops.file_move._1"))
    cfg_basicio.file_dir.file_ops.file_move._1

    """
    # s example : cfg_basicio.file_dir.file_ops.file_move._1
    if activity_name.startswith("spm."):
        activity_name = activity_name[4:]

    label_mapped = label_mapping(activity_name, "spm/spm_activity_labels.json")
    if label_mapped != activity_name:
        return label_mapped + "." + re.search(r'_\d+', activity_name.split()[-1]).group()
    else:
        return activity_name




def get_input_entity(right: str) -> List[dict]:
    """Get input Entity if possible else return None

    # called if left has no parameter AND  right match with conf.PATH_REGEX and with conf.FILE_REGEX, example :
    'matlabbatch{4}.spm.stats.fmri_spec.sess.multi = {
    '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/PREPROCESSING/ONSETS/sub-01-MultiCond.mat'};"

    Parameters
    ----------
    right : right side of ' = '

    Returns
    -------
     dict[str, str]
        else with key "@id", "label", "prov"

    """

    drop_brace = re.sub(r"[{};]", "", right)  # removes "{'" at the beginning and "'};" at the end
    file_list = drop_brace.split("',")  # split if multiple files
    entities = list()

    for file_str in file_list:
        if not file_str == "":
            file_drop_quotes = re.sub(r"\'", "", file_str)  # 'ds000052/RESULTS/Sub01/con_0001.nii,1'
            file_location = re.sub(r"\,1", "", file_drop_quotes)  # ds000052/RESULTS/Sub01/con_0001.nii
            entity_label_short = "_".join(file_location.split("/")[-2:])  # Sub01_con_0001.nii
            entity = {
                "@id": "urn:" + get_id(),
                "label": label_mapping(entity_label_short, "spm/spm_activity_labels.json"),
                "prov:atLocation": file_location
            }
            relative_path = os.path.abspath('./bids_prov/tests/samples_test/' + file_location)
            # this_path = os.path.abspath(__file__)

            if os.path.exists(relative_path):
                sha256_value = get_sha256(relative_path)
                checksum_name = "sha256_" + entity["@id"]
                entity['digest'] = {checksum_name: sha256_value}

            entities.append(entity)

    return entities


def readlines(filename: str) -> Generator[str, None, None]:  # from https://docs.python.org/3/library/typing.html
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
                    _line = _line[:-1]  # drop last in case of multiline,
                while _line.count("[") != _line.count("]"):  # case of multiline for 1 instruction  matlabbatch
                    _line = _line.strip() + " " + next(fd)[:-1].lstrip()  # append
                yield _line


def group_lines(lines: list) -> Dict[str, list]:
    """Group line by their activity id.  The activity id is between curly brackets, for every line

    Parameters
    ----------
    lines: iterable[str]
        lines to be grouped, where every element is a python string

    Returns
    -------
    dict[str, list]
        a mapping from activity id to lines belonging to this activity

    Example
    -------
    >>> from bids_prov.spm.spm_parser import group_lines
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
        new_key = f"{common_prefix}_{act_id}" if common_prefix[-1] == "." else f"{common_prefix}._{act_id}"  # add to
        # the common prefix the activity number
        new_res[new_key] = after_common_list  # keep the rest of the line
    # newres = {..., 'spm.stats.con._3':["spmmat(1) = cfg_dep('Model estimation: SP...;",
    #                                    "consess{1}.tcon.name = 'mr vs plain covariate';"
    #                                    ...], ...}
    return new_res


def get_entities_from_ext_config(conf_dic: dict, activity_name: str, activity_id: str) -> List[dict]:
    """ Get entities from external conf_dic (import yaml file)

    For example : spatial.preproc is contained in activity_name

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

    output_entities = list()
    for activity in conf_dic.keys():
        if activity in activity_name:
            # {'name': 'segment', 'outputs': ['c1xxx.nii.gz','c2xxx.nii.gz']}
            # act_preproc = next((activity for activity in records["prov:Activity"] if activity['@id'] == activity_id), None)
            for output in conf_dic[activity]['outputs']:
                name = conf_dic[activity]['name']
                entity = {"@id": "urn:" + get_id(),
                          "label": label_mapping(name, "spm/spm_activity_labels.json"),
                          "prov:atLocation": output,
                          "generatedBy": activity_id,
                          }
                output_entities.append(entity)
            # stop for loop at first match in if statement (match activity in conf_dic)
            break

    return output_entities  # empty list [] if no match,


def find_closest_activity(activities: list, right: str) -> dict:
    """Function to search dependent activity in right line. If found, find the corresponding activity
    in records_activities

    Parameters
    ----------
    activities : All previous activities
    right : current right end of line

    Returns
    -------
    closest_activity :  closest activity from current one, if exist , else None

    """
    # and retrieve the first parameter,  all digits between parenthesis
    dep_number = re.search(r"{(\d+)}", right) # retrieve name of the output_entity
    closest_activity = None
    for act in activities:
        if act["label"].endswith(dep_number.group(1)):
            closest_activity = act
            break

    return closest_activity

def find_output_id_from_closest(closest_activity: dict,records: dict) -> str:
    """ Find entity id, generated by the closest activity,

    Parameters
    ----------
    records :
    closest_activity :

    Returns
    -------
    output_id : entity id, if such one has been  generated by the closest activity, else new id
    """
    for entity in records["prov:Entity"]:
        if "generatedBy" in entity:
            if entity["generatedBy"] == closest_activity["@id"]: # entity["label"] == parts[-1]
                output_id = entity["@id"]
                break
    else:
        output_id = "urn:" + get_id()
    # output_id = next(
    #     (entity["@id"] for entity in records["prov:Entity"]
    #                   if parts[-1] == entity["label"] and entity["generatedBy"] == closest_activity["@id"]
    #     ), "urn:" + get_id()
    #     ) # find entity id generated by closest activity, if None new get_id

    return output_id


def mapping_label_entity(name_action,filename):
    """ Mapping function for entities in "cfg_dep('name_action': ..."

      Parameters
      ----------
      filename : input filename
      name_action : name of action in dependency action (cfg_dep)

      Returns
      -------
      label_entity :  label of entity

      """

    if 'SPM.mat' in name_action:
        label_entity = 'SPM.mat'
    elif  name_action == 'GunZip Files: GunZipped Files':
        label_entity = re.sub(".gz", '', filename)
    else:
        prefix_entity = label_mapping(name_action, "spm/spm_entity_labels.json")
        label_entity = prefix_entity + filename
    return label_entity


def find_entity_from_id(idx, entities):
    """ Function to find entity by id from the list of all entities"

      Parameters
      ----------
      idx : id to find
      entities : list of all entities

      Returns
      -------
      input_entity :  input entity if it exists, else None

      """
    input_entity = None # next((entity for entity in entities ), None)
    for entity in entities:
        if entity["@id"] == idx:
            input_entity = entity
            break

    return input_entity

def get_records(task_groups: dict, agent_id: str, verbose=False) -> dict:
    """Take the result of `group_lines` and output the corresponding  JSON-ld graph as a python dict

    Parameters
    ----------
    task_groups : task activities grouped by activity number
    agent_id : agent's uuid
    verbose : True to have more verbosity

    Returns
    -------
    dict[str, list]
        records : dict with key "@context", ... "records":{"prov:Agent": ..."prov:Activity":..."prov:Entity":....}

    """

    records = defaultdict(list)
    entities_ids = set()

    for i, (common_prefix_act, end_line_list) in enumerate(task_groups.items()):

        # Regeneration of the command
        command = ""
        command_prefix = f"matlabbatch{{{i+1}}}." + re.sub("_\d+", "", common_prefix_act)
        if len(end_line_list) == 1:  # if only one line in a batch, delete the dot at the end of the prefix
            command_prefix = command_prefix[:-1]
        for c in end_line_list:
            command += command_prefix + c + "\n"

        activity_id = "urn:" + get_id()
        activity = {"@id": activity_id,
                    "label": format_activity_name(common_prefix_act),
                    "used": list(),
                    "associatedWith": "urn:" + agent_id,
                    "command": command
                    }

        output_entities, input_entities, params = list(), list(), {}
        output_ext_entities = get_entities_from_ext_config(conf.static["activities"], common_prefix_act, activity_id)
        output_entities.extend(output_ext_entities)
        add_ext_entity = 0
        for end_line in end_line_list:
            # split in 2 at the level of the equal the rest of the action
            left, right = end_line.split(" = ")

            if not conf.has_parameter(left)  and re.search(conf.PATH_REGEX, right) and re.search(conf.FILE_REGEX, right):

                # left has no parameter AND  right match with conf.PATH_REGEX and with conf.FILE_REGEX
                in_entity = get_input_entity(right)
                input_entities.extend(in_entity)

            elif (conf.has_parameter(left) or conf.has_parameter(common_prefix_act)) \
                    and any(["substruct" in l for l in [common_prefix_act, left, right]]):

                dependency = re.search(conf.DEPENDENCY_REGEX, right, re.IGNORECASE)  # cfg_dep\(['"]([^'"]*)['"]\,.*
                # check if the line call cfg_dep and retrieve the first parameter retrieve all digits between parenthesis
                # or has_parameter(common_prefix_act) is mandatory because if in our activity we have only one call
                # to a function, the common part will be full and so left will be empty
                if dependency is not None :
                    name_cfg_dep = str(dependency.group(1))
                    closest_activity = find_closest_activity(records["prov:Activity"], right)
                    output_id = find_output_id_from_closest(closest_activity, records)
                    activity["used"].append(output_id)
                    # adds to the current activity the fact that it has used the previous entity
                    #
                    if output_ext_entities and add_ext_entity == 0:
                        for idx, entity in enumerate(output_ext_entities):
                            input_ent = find_entity_from_id(output_id, records["prov:Entity"])
                            entity['label'] = f"{entity['label']}{str(idx + 1)}"
                            entity['prov:atLocation'] = f"c{str(idx+1)}{input_ent['label']}"
                        add_ext_entity = 1

                 # TO DO whatif multiple
                    if closest_activity["used"]:
                        id_closest = closest_activity["used"][0]
                        input_entity = find_entity_from_id(id_closest, records["prov:Entity"])
                        filename = input_entity['label']
                    else:
                        filename = '' # for activity that creates SPM.mat
                    out_label = mapping_label_entity(name_cfg_dep, filename)

                    output_entity = { # output for closest activity but input for current one
                        "@id": output_id,
                        "label":  out_label , #label_mapping(parts[-1], "spm/spm_labels.json"),
                        # "prov:atLocation": TODO
                        "generatedBy": closest_activity["@id"],
                    }
                    output_entities.append(output_entity)

                else:  # dependency is None no r"(d+)"
                    Warning(f"Could not parse line with dependency {right}")
                    continue  # break to for common_prefix_act,

            else:  # Not if in_entity and Not   (conf.has_parameter(left) ....)

                param_name = left.strip()
                right_ = right[:-1]  # remove ";" at the end of right
                param_value = right_ if not right_.startswith("[") else right_.replace(" ", ", ")
                params[param_name] = param_value  # example : [4 2] becomes [4, 2]

        if params:
            activity["parameters"] = params

        if input_entities:
            used_entities = [entity["@id"] for entity in input_entities]
            activity["used"].extend(used_entities) # we add entities from input_entities


        entities = input_entities + output_entities

        for entity in entities:
            if entity["@id"] not in entities_ids:
                records["prov:Entity"].append(entity) # ADD entity if not present
            entities_ids.add(entity["@id"])

        records["prov:Activity"].append(activity) # ADD activity



    return records


def spm_to_bids_prov(filename: str, context_url=CONTEXT_URL, output_file=None, spm_ver="SPM12r7224", verbose=False,
                     indent=2) -> None:
    """ Exporter from batch.m to an output jsonld

    Parameters
    ----------
    spm_ver : version of SPM , SPM 12 release 7224 by default
    filename : str
        input file of batch.m; example filename = "/test/spm_batch.m"
    context_url : str, optional
        url of context, by default CONTEXT_URL
    output_file : str, optional
        if None, default is filename with jsonld extension = "/test/spm_batch.jsonld"
    verbose : bool, optional
        False with less verbosity by default
    indent : int, optional
        2, number of indentation in jsonfile between each object
    """

    graph, agent_id = get_default_graph(label="SPM", context_url=context_url, soft_ver=spm_ver)
    lines = readlines(filename)
    tasks = group_lines(lines)  # same as list(lines) to expand generator
    records = get_records(tasks, agent_id, verbose=verbose)
    graph["records"].update(records)


    for activity in records["prov:Activity"]:  # Remove each activity number from the activity labels
        activity["label"] = re.sub(r'._\d+$', '', activity["label"])

    if output_file is None:
        output_file = os.path.splitext(filename)[0] + '.jsonld'  # replace extension .m by .jsonld

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="./examples/spm_default/batch.m", help="data dir where batch.m are researched")
    parser.add_argument("--output_file", type=str, default="./examples/spm_default/batch.jsonld", help="output dir where results are written")
    parser.add_argument("--context_url", default=CONTEXT_URL, help="CONTEXT_URL")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    spm_to_bids_prov(opt.input_file, context_url=opt.context_url, output_file=opt.output_file, verbose=opt.verbose)
    # > python -m   bids_prov.spm.ls spm_parser --input_file ./nidm-examples/spm_2_t_test/batch.m --output_file  ./spm_2_t_test.jsonld
