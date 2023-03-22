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


def _get_kwarg(serie,  with_value=True):
    arg_list = []

    add_argument_list = []
    for u_arg in serie:
        if type(u_arg) == dict:
            # parser.add_argument(u_arg["name"], nargs='+', action='append')
            if "nargs" in u_arg:
                add_argument_list.append(
                    {"arg": u_arg["name"], "nargs": u_arg["nargs"], "action": 'append'})
            else:
                add_argument_list.append(
                    {"arg": u_arg["name"], "nargs": "+", "action": 'append'})
            arg_list.append((u_arg["name"], [u_arg["index"]]))
        if type(u_arg) == str and ":" not in u_arg:

            if with_value:
                if u_arg == ">" or u_arg == ">>":
                    # parser.add_argument("-" + u_arg)
                    add_argument_list.append({"arg": "-" + u_arg})
                    arg_list.append(("-" + u_arg, [0]))
                else:
                    # parser.add_argument(u_arg)
                    add_argument_list.append({"arg": u_arg})
                    arg_list.append((u_arg, [0]))

            else:
                if u_arg == ">" or u_arg == ">>" or u_arg == "|&":
                    # print("with_novalue > u_arg", u_arg)
                    # parser.add_argument(u_arg, action='store_true')
                    add_argument_list.append(
                        {"arg": "-" + u_arg, "action": 'store_true'})
                    arg_list.append(("-" + u_arg, []))
                else:
                    add_argument_list.append(
                        {"arg": u_arg, "action": 'store_true'})
                    arg_list.append((u_arg, []))

    return add_argument_list, arg_list


def _get_arg(serie, arg_rest):
    arg_list = []
    arg_purge = [arg for arg in arg_rest if not arg.startswith("-")]
    for u_arg in serie:
        if type(u_arg) == int:
            # print("arg_purge", type(arg_purge), arg_purge, u_arg)
            if u_arg < len(arg_purge):
                arg_list.append(arg_purge[u_arg])

        if type(u_arg) == str and ":" in u_arg:
            res = eval("arg_purge[" + u_arg + "]")
            arg_list.extend(res) if type(res) == list else arg_list.append(res)

    return arg_list


def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
        # If string is not a valid `float`,
        # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True


def _get_entities_from_kwarg(entities, opts, parse_kwarg):
    for u_arg in parse_kwarg:
        param = u_arg[0]
        index = u_arg[1]
        value = []
        for (arg, val) in opts._get_kwargs():
            # print("\n--arg, val", type(arg), type(val), arg, val)
            if param.split("-")[1] == arg:
                # print("\n----arg select", type(arg), arg)
                if val != None:
                    # print("\n------val != None", type(val), val)
                    if type(val) == list:
                        # print("\n--------val == list", type(val), val)
                        for info in val:
                            # print("\n----------info in val", type(info), info)
                            for i in index:
                                # print("\n------------i in indexn info", type(i), i)
                                if type(i) != list:
                                    # print("\n--------------i != list", type(i), i)
                                    res = eval("info[" + str(i) + "]")
                                    value.extend(res) if type(
                                        res) == list else value.append(res)
                                else:
                                    for j in i:
                                        # print(
                                        #     "\n----------------i == list : j",
                                        #     type(j),
                                        #     j,
                                        #     "info[" + str(j) + "]",
                                        #     eval("info[" + str(j) + "]"))
                                        res = eval("info[" + str(j) + "]")
                                        value.extend(res) if type(
                                            res) == list else value.append(res)

                    else:
                        if not is_number(val):
                            value.append(val)
        if len(value) > 0:
            entities.extend(value)
    return entities


def get_entities(cmd_s, parameters):
    """
    Given a list of command arguments `cmd_s` and a dict of `parameters`, this function returns the entities associated
    with the parameters.

    Parameters
    ----------

    cmd_s : list of str
        A list of command arguments.
    parameters : Dict
        Dict of parameters loaded by the description_functions.json to search for in `cmd_s`. 

    Returns
    -------
    inputs, outputs, params :  of entities associated with the parameters.

    Example
    -------

    >>> df = {
            "name": "command",
            "used": [0, "-a"],
            "generatedBy": [-1, "-b"]
        }
    >>> cmd_s = ["command", "-a", "kwarg_0", "arg_0", "arg_1",  "-b", "kwarg_1"]
    >>> inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    >>> (["kwarg_0", "arg_0"], ["kwarg_1", "arg_1"], [])

    """

    parser = argparse.ArgumentParser(
        add_help=False, conflict_handler='resolve')

    inputs_kwarg = []
    outputs_kwarg = []
    parameters_value = []
    parameters_no_value = []

    # print("\n\n cmd_s", cmd_s)
    # change cmd_s to add ">" , ">>", "|&"  as parameter for argparse
    cmd_s = ["->" if it == ">" else it for it in cmd_s]
    cmd_s = ["->>" if it == ">>" else it for it in cmd_s]
    cmd_s = ["-|&" if it == "|&" else it for it in cmd_s]

    # print("\n\n cmd_s change", cmd_s)

    if "used" in parameters:
        add_argument_list, inputs_kwarg = _get_kwarg(
            parameters["used"])
        for kwarg in add_argument_list:
            arg = kwarg.pop("arg")
            parser.add_argument(arg, **kwarg)

    if "generatedBy" in parameters:
        add_argument_list, outputs_kwarg = _get_kwarg(
            parameters["generatedBy"])
        for kwarg in add_argument_list:
            arg = kwarg.pop("arg")
            parser.add_argument(arg, **kwarg)

    if "parameters_value" in parameters:
        add_argument_list, parameters_value = _get_kwarg(
            parameters["parameters_value"])
        for kwarg in add_argument_list:
            arg = kwarg.pop("arg")
            parser.add_argument(arg, **kwarg)

    if "parameters_no_value" in parameters:
        add_argument_list, parameters_no_value = _get_kwarg(
            parameters["parameters_no_value"], with_value=False)
        for kwarg in add_argument_list:
            arg = kwarg.pop("arg")
            parser.add_argument(arg, **kwarg)

    opts, arg_rest = parser.parse_known_args(cmd_s)

    # print("\n\n parameters", parameters)
    # print("\n\n parse_known_args", opts)
    # print("\n\n inputs_kwarg", inputs_kwarg)
    # print("\n\n outputs_kwarg", outputs_kwarg)
    # print("\n\n parameters_value", parameters_value)
    # print("\n\n parameters_no_value", parameters_no_value)
    # print("\n\n arg_rest", arg_rest)

    entities = []
    arg_in_param = []

    inputs = []
    outputs = []
    params = []
    inputs = _get_entities_from_kwarg(inputs, opts, inputs_kwarg)
    outputs = _get_entities_from_kwarg(outputs, opts, outputs_kwarg)
    params = _get_entities_from_kwarg(params, opts, parameters_value)
    params = _get_entities_from_kwarg(params, opts, parameters_no_value)

    if "used" in parameters:
        inputs.extend(_get_arg(parameters["used"], arg_rest))

    if "generatedBy" in parameters:
        outputs.extend(_get_arg(parameters["generatedBy"], arg_rest))

     # print("\n\n inputs", inputs)
    # print("\n\n outputs", outputs)
    # print("\n\n params", params)

    return inputs, outputs, params


def build_records(groups: Mapping[str, List[str]], agent_id: str):
    """
    Build the `records` field for the final .jsonld file,
    from commands lines grouped by stage (e.g. `Registration`, `Post-stats`)

    Returns
    -------
    dict: a set of records compliant with the BIDS-prov standard
    """
    records = defaultdict(list)

    filepath = os.path.join(os.path.dirname(__file__),
                            "description_functions.json")
    with open(filepath) as f:
        description_functions = json.load(f)

    for k, v in groups.items():
        # print(k, ":", v)
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
                    description_of_command = df
                    function_in_description_functions = True
                    inputs, outputs, parameters = get_entities(
                        cmd_s[1:], description_of_command)
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
                inputs = list(chain(*(attributes.pop(k)
                              for k in attributes.keys() & INPUT_TAGS)))
                # same process with OUTPUT_TAGS
                outputs = list(chain(*(attributes.pop(k)
                               for k in attributes.keys() & OUTPUT_TAGS)))
                entity_names = [_ for _ in re.findall(
                    INPUT_RE, cmd_without_attributes[len(a_name):])]

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

            # the file name and possible extension
            label = f"{os.path.split(a_name)[1]}"

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

    graph, agent_id = get_default_graph(
        label="FSL", context_url=context_url, soft_ver=soft_ver)

    lines = readlines(filename)
    records = build_records(lines, agent_id)
    graph["records"].update(records)

    with open(output_file, "w") as fd:
        json.dump(graph, fd, indent=indent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str,
                        default="./examples/fsl_default/report_log.html", help="fsl execution log file")
    parser.add_argument("--output_file", type=str, default="./examples/fsl_default/report_log.jsonld",
                        help="output dir where results are written")
    parser.add_argument(
        "--context_url", default=CONTEXT_URL, help="CONTEXT_URL")
    parser.add_argument("--verbose", action="store_true", help="more print")
    opt = parser.parse_args()

    fsl_to_bids_prov(opt.input_file, context_url=opt.context_url,
                     output_file=opt.output_file, verbose=opt.verbose)
    # visualize(opt.output_file, output_file="res.png")

    # #
    # input_file = os.path.abspath("../../examples/from_parsers/fsl/fsl_full_examples001_report_log.html")
    # output_file = "../../res.jsonld"
    # random.seed(14)
    # fsl_to_bids_prov(input_file, context_url=CONTEXT_URL, output_file=output_file, verbose=False)
