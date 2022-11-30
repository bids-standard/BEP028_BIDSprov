import sys
import click
import json
import os
import re

from collections import defaultdict
from bids_prov import spm_load_config as conf
from bids_prov import get_id


def format_activity_name(s: str, l=30) -> str:
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
    if verbose:
        print(f"left : {left}")
        print(f"right : {right}")
    if conf.has_parameter(left):  # r"[^\.]+\(\d+\)"
        # a string contains at least one parameter if it does not start with a dot and contains at least one digit
        # between brackets.
        # if there are parameters, they are necessarily in the left part (function call) and this is not an entity
        if verbose:
            print("the string contains parameters so this is not an input_entity")
        return None
    if not next(re.finditer(conf.PATH_REGEX, right), None):
        # r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
        # if not None (if it doesn't match with conf.PATH_REGEX), enter in if
        if verbose:
            print("the string does not match with conf.PATH_REGEX")
        return None
    if not next(re.finditer(conf.FILE_REGEX, right), None):
        # r"(\.[a-z]{1,3}){1,2}"
        # the string does not contain a filename extension so this is not an entity
        if verbose:
            print("the string does not contain a filename so this is not an input_entity")
        return None

    entity_label = re.sub(r"[{};\'\"]", "", right).split("/")[-1]  # sub allows you to remove braces; apostrophe and
    # quotation mark.
    # If we have : "$HOME/nidmresults-examples/spm_default/ds011/sub-01/func/sub-01_task-tonecounting_bold.nii.gz",
    # the line will return "sub-01_task-tonecounting_bold.nii.gz" and not "sub-01_task-tonecounting_bold.nii.gz'};"

    entity = {
        "@id": "niiri:" + entity_label + get_id(),
        "label": entity_label,
        "prov:atLocation": right[2:-3],  # similar processing with respect to the entity_label variable. The line
        # removes "{'" at the beginning and "'};" at the end
    }
    if verbose:
        print(f"entity : {entity}")
    return entity


def preproc_param_value(val: str) -> str:
    if val[0] == "[":  # example : [4 2] becomes [4, 2]
        return val.replace(" ", ", ")
    return val


def readlines(filename: str):  # -> Generator[str, None, None]  from https://docs.python.org/3/library/typing.html
    """Read lines from the original batch.m file

    A definition should be associated with a single line in the output
    """
    cnt = 0
    with open(filename) as fd:
        for line in fd:
            if line.startswith("matlabbatch"):
                _line = line[:-1]  # remove "\n"
                while _line.count("{") != _line.count("}"):
                    _line += next(fd)[:-1].lstrip() + ","
                    # TODO error sur covariate matlabbatch{# 1}.spm.stats.factorial_design.des.t1.scans "," at end
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
    # example: in batch.m of spm12:
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


def get_entities_from_ext_config(conf_dic, activity_name, activity_id):
    # checks if spatial.preproc is contained in the name of the current activity and if so returns
    # spatial.preproc

    # REMI like :conf_outputs = next((k for k in conf_dic if k in activity_n), None)
    # if conf_outputs is not None:
    # activity_name = conf_outputs["name"]  # FIXME ? useless ?
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


def get_records(task_groups: dict, records=defaultdict(list), verbose=False) -> dict:
    """Take the result of `group_lines` and output the corresponding
    JSON-ld graph as a python dict

    See Also
    --------
    bids_prov.spm_parser.group_lines
    """

    entities_ids = set()
    if verbose:
        print(f"task_groups : {task_groups}")
    for common_prefix_act, end_line_list in task_groups.items():

        activity_id = "niiri:" + common_prefix_act + get_id()
        activity = {
            "@id": activity_id,
            "label": format_activity_name(common_prefix_act),
            "used": list(),
            "wasAssociatedWith": "RRID:SCR_007037",  # TODO ?
        }
        if verbose:
            print("-" * 50)
            print(f"activity : {activity}, values : {task_groups[common_prefix_act]}")
        output_entities, input_entities = list(), list()

        output_ext_entities = get_entities_from_ext_config(conf.static["activities"], common_prefix_act, activity_id)
        output_entities.extend(output_ext_entities)
        params = {}

        for end_line in end_line_list:
            split = end_line.split(" = ")  # split in 2 at the level of the equal the rest of the action
            if len(split) != 2:
                print(f"could not parse with '... = ... ' {end_line}")
                continue

            left, right = split
            in_entity = get_input_entity(left, right, verbose=verbose)

            if in_entity:
                input_entities.append(in_entity)

            elif (conf.has_parameter(left) or conf.has_parameter(common_prefix_act)) \
                    and any(["substruct" in l for l in [common_prefix_act, left, right]]):
                # or has_parameter(common_prefix_act) is mandatory because if in our activity we have only one call
                # to a function, the common part will be full and so left will be empty
                dependency = re.search(conf.DEPENDENCY_REGEX, right, re.IGNORECASE)  # cfg_dep\(['"]([^'"]*)['"]\,.*
                # check if the line call cfg_dep and retrieve the first parameter
                dep_number = re.search(r"{(\d+)}", right)  # retrieve all digits between parenthesis

                if dependency is not None:

                    parts = dependency.group(1).split(": ")  # retrieve name of the output_entity
                    # if right = "cfg_dep('Move/Delete Files: Moved/Copied Files', substruct('.',...));"
                    # return : ['Move/Delete Files', 'Moved/Copied Files']
                    # closest_activity_REMY = next(filter(lambda a: a["label"].endswith(dep_number.group(1)),
                    #                                records["prov:Activity"], ),
                    #                         None, )
                    # among all the activities, check if one of them has a label ending with "dep_number" and
                    # return the activity

                    closest_activity = None
                    for act in records["prov:Activity"]:
                        if act["label"].endswith(dep_number.group(1)):
                            closes_activity2 = act
                            break

                    # REMI like
                    if closest_activity is None:
                        continue  # break for loop end_line in end_line_list

                    if verbose:
                        print(f"records : {records}")
                        print(f"closest_activity : {closest_activity}")

                    output_id = ("niiri:" + parts[-1].replace(" ", "") + dep_number.group(1))
                    # example : "niiri:oved/CopiedFiles1
                    activity["used"].append(output_id)  # adds to the current activity the fact that it has used the
                    # previous entity

                    output_entities.append({
                        "@id": output_id,
                        "label": parts[-1],
                        # "prov:atLocation": TODO
                        "wasGeneratedBy": closest_activity["@id"],
                    })
                else:  # dependency is None no r"(d+)"
                    Warning(f"Could not parse line with dependency {end_line}")

            else:  # Not if in_entity and Not   (conf.has_parameter(left) ....)
                param_name = ".".join(left.split(".")[-2:])  # split left by "." and keep the two last elements
                param_value = preproc_param_value(right[:-1])  # remove ";" at the end of right
                if verbose:
                    print("params")
                    print(param_name, param_value)
                # HANDLE STRUCTS eg. struct('name', {}, 'onset', {}, 'duration', {})
                # if param_value.startswith("struct"):
                #     continue  # TODO handle dictionary-like parameters

                try:  # TODO why use of exceptions
                    eval(param_value) # Convert '5' to 5
                except:
                    Warning(f"could not set {param_name} to {param_value}")
                    continue
                finally:
                    # params.append([param_name, param_value])
                    params[param_name] = param_value

        if input_entities:
            used_entities = [e["@id"] for e in input_entities]
            if verbose:
                print(f"input_entities : {input_entities}")
                print(f'activity["used"] : {activity["used"]}')
            activity["used"] = (activity["used"] + used_entities)  # we add entities from input_entities
        entities = input_entities + output_entities

        if params:
            activity["parameters"] = params

        records["prov:Activity"].append(activity)
        for e in entities:
            if e["@id"] not in entities_ids:
                records["prov:Entity"].append(e)
            entities_ids.add(e["@id"])

    return records


@click.command()
@click.argument("filenames", nargs=-1)
@click.option("--output-file", "-o", required=True)
@click.option("--context-url", "-c", default=conf.CONTEXT_URL, )
@click.option("--verbose", default=False)
def spm_to_bids_prov(filenames, output_file: str, context_url: str, verbose: bool) -> None:
    filename = filenames[0]  # FIXME
    graph = conf.get_empty_graph(context_url=context_url)

    lines = readlines(filename)
    tasks = group_lines(lines)  # same as list(lines) to expand generator
    records = get_records(tasks, verbose=verbose)
    graph["records"].update(records)

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=2)

    return graph


if __name__ == "__main__":
    sys.exit(spm_to_bids_prov())
    # Example command  with CLI:
    # python -m bids_prov.spm_parser -o res.jsonld ./examples/spm_default/batch.m --verbose=True

    # temporary test without click
    # filenames = ['../batch_example_spm.m',
    #              '../nidm-examples/spm_covariate/batch.m',
    #              './tests/batch_test/SpatialPreproc.m',
    #              '../spm_HRF_informed_basis/batch.m']
    # output_file = '../batch_example_spm.jsonld'
    # CONTEXT_URL = "https://raw.githubusercontent.com/cmaumet/BIDS-prov/context-type-indexing/context.json"
    # # UTLISIER CLICK https://zetcode.com/python/click/
    # graph = spm_to_bids_prov(filenames[0], output_file, CONTEXT_URL, verbose=False)
    # lines = readlines(filenames[0])
    # print(*list(lines), sep='\n')

