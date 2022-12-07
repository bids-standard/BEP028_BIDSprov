import sys

# import click
import argparse
import json
import os
import re

from collections import defaultdict
from bids_prov import spm_load_config as conf
from bids_prov import get_id


def format_activity_name(s: str, l=40) -> str:
    # s example : cfg_basicio.file_dir.file_ops.file_move._1
    if s.startswith("spm."):
        s = s[4:]
    tmp = s.split(".")  # ['cfg_basicio', 'file_dir', 'file_ops', 'file_move', '_1']
    while sum(map(len, tmp)) > l:  # sum of the lengths of each element of tmp
        tmp = tmp[1:]
    return ".".join(tmp)  # file_dir.file_ops.file_move._1


def get_input_entity(left: str, right: str, verbose=False) -> (None | dict):
    """get input Entity if possible else return None
    Very few entities in detectable inputs. We find for example the read files.

    left: string
        left side of ' = '
    right: string
        right side of ' = '
    """
    if conf.has_parameter(left):  # r"[^\.]+\(\d+\)"
        # a string contains at least one parameter if it does not start with a dot and contains at least one digit
        # between brackets.
        # if there are parameters, they are necessarily in the left part (function call) and this is not an entity
        if verbose:
            print("the string contains parameters so this is not an input_entity")
        return None
    # if not next(re.finditer(conf.PATH_REGEX, right), None):  # Remi like
    if not re.search(conf.PATH_REGEX, right):  # r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
        # if not None (if it doesn't match with conf.PATH_REGEX), enter in if
        if verbose:
            print("the string does not match with conf.PATH_REGEX")
        return None
    if not re.search(conf.FILE_REGEX, right): # r"(\.[a-z]{1,3}){1,2}"
        # the string does not contain a filename extension so this is not an entity
        if verbose:
            print("the string does not contain a filename so this is not an input_entity")
        return None

    entity_label = re.sub(r"[{};\'\"]", "", right)  # sub allows you to remove braces; apostrophe and  quotation mark.
    entity_label = entity_label.split("/")[-1]
    # If we have : "$HOME/nidmresults-examples/spm_default/ds011/sub-01/func/sub-01_task-tonecounting_bold.nii.gz",
    # the line will return "sub-01_task-tonecounting_bold.nii.gz" and not "sub-01_task-tonecounting_bold.nii.gz'};"

    entity = {
        "@id": "niiri:" + entity_label + get_id(),
        "label": entity_label,
        "prov:atLocation": right[2:-3],  # similar processing with respect to the entity_label variable. The line
        # removes "{'" at the beginning and "'};" at the end
    }

    return entity


def readlines(filename: str):  # -> Generator[str, None, None]  from https://docs.python.org/3/library/typing.html
    """Read lines from the original batch.m file

    A definition should be associated with a single line in the output
    """
    cnt = 0 # TODO count activity here or in another function
    with open(filename) as fd:
        for line in fd:
            if line.startswith("matlabbatch"):
                _line = line[:-1]  # remove "\n"
                brace_with_multiline = False
                while _line.count("{") != _line.count("}"):
                    brace_with_multiline = True
                    _line += next(fd)[:-1].lstrip() + ","  # TODO not cover by test
                    # TODO error sur covariate matlabbatch{# 1}.spm.stats.factorial_design.des.t1.scans "," at end
                if brace_with_multiline:
                    _line = _line[-1] #drop last ,
                while _line.count("[") != _line.count("]"):  # case of multiline for 1 instruction  matlabbatch
                    _line = _line.strip() + " " + next(fd)[:-1].lstrip()  # append
                # print(_line)
                yield _line


def group_lines(lines: list) -> dict:
    """Group line by their activity id

    The activity id is between curly brackets, for every line

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
    # return

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
    # checks if spatial.preproc is contained in the name of the current activity and if so returns spatial.preproc
    #
    # REMI like :conf_outputs = next((k for k in conf_dic if k in activity_n), None)
    # if conf_outputs is not None:
    # activity_name = conf_outputs["name"]
    # conf_outputs = conf_dic[conf_outputs]
    output_entities = list()
    for activity in conf_dic.keys():
        if activity in activity_name:
            for output in conf_dic[activity]:
                output_entities.append(
                    {"@id": output + get_id(),
                     "label": output,
                     "prov:atLocation": output,
                     "wasGeneratedBy": activity_id,
                     }
                )
            break  # stop for loop at first math in if statement (match activity)

    return output_entities  # empty list [] if no match,

def dependency_process(records: dict, activity: dict, right: str, end_line: str, verbose=False) -> tuple:
    # or has_parameter(common_prefix_act) is mandatory because if in our activity we have only one call
    # to a function, the common part will be full and so left will be empty
    dependency = re.search(conf.DEPENDENCY_REGEX, right, re.IGNORECASE)  # cfg_dep\(['"]([^'"]*)['"]\,.*
    # check if the line call cfg_dep and retrieve the first parameter
    dep_number = re.search(r"{(\d+)}", right)  # retrieve all digits between parenthesis
    output_entity = {}
    closest_activity = None
    if dependency is not None:
        parts = dependency.group(1).split(": ")  # retrieve name of the output_entity
        # if right = "cfg_dep('Move/Delete Files: Moved/Copied Files', substruct('.',...));"
        # return : ['Move/Delete Files', 'Moved/Copied Files']

        for act in records["prov:Activity"]:
            if act["label"].endswith(dep_number.group(1)):
                closest_activity = act
                output_id = ("niiri:" + parts[-1].replace(" ", "") + dep_number.group(1))  # example : "niiri:oved/CopiedFiles1

                activity["used"].append(output_id)  # adds to the current activity the fact that it has used the previous entity
                output_entity = {"@id": output_id,
                                 "label": parts[-1],
                                 # "prov:atLocation": TODO
                                 "wasGeneratedBy": closest_activity["@id"],
                }
            if verbose:
                print(f"records : {records} \n closest_activity : {closest_activity}")
    else:  # dependency is None no r"(d+)" # TODO not cover by test

        Warning(f"Could not parse line with dependency {end_line}")
    return closest_activity, output_entity

def get_records(task_groups: dict, records=None, verbose=False) -> dict:
    """Take the result of `group_lines` and output the corresponding
    JSON-ld graph as a python dict

    See Also
    --------
    bids_prov.spm_parser.group_lines
    """

    if records is None:
        records = defaultdict(list)
    if verbose:
        print(f"task_groups : {task_groups}")

    entities_ids = set()

    for common_prefix_act, end_line_list in task_groups.items():

        activity_id = "niiri:" + common_prefix_act + get_id()
        activity = {"@id": activity_id,
                    "label": format_activity_name(common_prefix_act),
                    "used": list(),
                    "wasAssociatedWith": "RRID:SCR_007037",  # TODO ?
        }
        if verbose:
            print("-" * 50)
            print(f"activity : {activity}, values : {task_groups[common_prefix_act]}")
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
            print(left, '=', right)
            in_entity = get_input_entity(left, right, verbose=verbose)

            if in_entity:
                print('-> in  entity')
                input_entities.append(in_entity)

            elif (conf.has_parameter(left) or conf.has_parameter(common_prefix_act)) \
                    and any(["substruct" in l for l in [common_prefix_act, left, right]]):

                closest_activity, output_entity = dependency_process(records, activity, right, end_line, verbose=verbose)

                if closest_activity is None:
                    continue
                else:
                    output_entities.append(output_entity)

            else:  # Not if in_entity and Not   (conf.has_parameter(left) ....)
                # def param_process(left,right,verbose=False): TODO

                param_name = ".".join(left.split(".")[-2:])  # split left by "." and keep the two last elements
                right_= right[:-1]  # remove ";" at the end of right
                param_value = right_ if not right_.startswith("[") else right_.replace(" ", ", ")
                # example : [4 2] becomes [4, 2]
                # FIXME
                if verbose:
                    print("params", param_name, param_value)
                # HANDLE STRUCTS eg. struct('name', {}, 'onset', {}, 'duration', {})
                # if param_value.startswith("struct"):
                #     continue  # TODO handle dictionary-like parameters

                try:  # TODO why use of exceptions
                    eval(param_value)  # Convert '5' to 5
                    # print(f"ok {param_value}")

                except:
                    print(f"POP {param_value}  \n")
                    Warning(f"could not set {param_name} to {param_value}")
                    # "struct('name', {}, 'levels', {})" dans batch_example_spm
                    # Inf dans spm_HRF_informed_basis
                    # FIXME spm_non_sphericity
                    #  if right {'/storage/essicdULTS/Sub01/CanonicalHRF/con_0001.nii,1', ........};,
                    #  param_value still have an extra ;


                finally:
                    params[param_name] = param_value

                    # params.append([param_name, param_value])

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


# @click.command()
# @click.argument("filename", nargs=-1)
# @click.option("--output-file", "-o", required=True)
# @click.option("--context-url", "-c", default=conf.CONTEXT_URL, )
# @click.option("--verbose", default=False)
def spm_to_bids_prov(filename: str, context_url=conf.CONTEXT_URL, output_file=None, verbose=False, indent=2) -> None:
    """
    Exporter from batch.m to an output jsonld

    """
    # filename = filename[0]  # FIXME
    graph = conf.get_empty_graph(context_url=context_url)

    lines = readlines(filename)
    tasks = group_lines(lines)  # same as list(lines) to expand generator
    records = get_records(tasks, verbose=verbose)
    graph["records"].update(records)

    if output_file is None:
        output_file = os.path.splitext(filename)[0] + '.jsonld'  # replace extension .m by .jsonld

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)


if __name__ == "__main__":
    # sys.exit(spm_to_bids_prov())
    # Example command  with CLI:
    # python -m bids_prov.spm_parser  ./examples/spm_default/batch_covariate.m  -o res.jsonld --verbose=False

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="./examples/spm_default/batch.m",
                        help="data dir where batch.m are researched")
    parser.add_argument("--output_file", type=str, default="res.jsonld", help="output dir where results are written")
    parser.add_argument("--context_url", default=conf.CONTEXT_URL, help="CONTEXT_URL")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    spm_to_bids_prov(opt.input_file, context_url=opt.context_url, output_file=opt.output_file, verbose=opt.verbose)

    # temporary test without parser
    # filenames = ['./tests/samples_test/batch_example_spm.m',
    #              './tests/samples_test/partial_conjunction.m',
    #              '../nidm-examples/spm_HRF_informed_basis/batch.m',
    #              '../nidm-examples/spm_explicit_mask/batch.m',
    #              '../nidm-examples/spm_full_example001/batch.m', # fr closest None
    #              '../nidm-examples/spm_non_sphericity/batch.m',
    #              '../nidm-examples/spm_HRF_informed_basis/batch.m',
    #            ]
    # output_file = '../res_temp.jsonld'
    # for filename in filenames[-2:-1]:
    #     print(filename + '\n')
    #     spm_to_bids_prov(filename, output_file=output_file)

    # nidm_samples = os.listdir('../nidm-examples/')
    # spm_samples = [s for s in nidm_samples if s.startswith('spm')]
    # # for spm_sample in spm_samples:
    #     print('\n' + spm_sample + '\n')
    #     spm_to_bids_prov(f"../nidm-examples/{spm_sample}/batch.m", output_file=output_file)
