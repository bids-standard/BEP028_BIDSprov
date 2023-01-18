import re
import yaml
import os
import hashlib

# contains the path from home to the directory where this script is located
this_path = os.path.dirname(os.path.abspath(__file__))

PATH_REGEX = r"([A-Za-z]:|[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*)((/[A-Za-z0-9_.-]+)+)"
PARAM_REGEX = r"[^\.]+\(\d+\)"  # example: some_activity.function(53)
FILE_REGEX = r"(\.[a-z]{1,3}){1,2}"  # the string does not contain a filename so this is not an input_entity
DEPENDENCY_REGEX = r"""cfg_dep\(['"]([^'"]*)['"]\,.*"""  # TODO : add ": " in match


def has_parameter(line):
    return re.search(PARAM_REGEX, line) is not None
# has_entity = lambda line: not has_parameter(line) and next(re.finditer(PATH_REGEX, line), None) is not None


with open(this_path + "/spm_config.yml", "r") as fd:
    static = yaml.load(fd, Loader=yaml.CLoader)
