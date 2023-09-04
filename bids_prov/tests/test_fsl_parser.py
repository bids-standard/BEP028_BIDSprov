from bids_prov.fsl.fsl_parser import INPUT_RE, ATTRIBUTE_RE, readlines, get_entities
from unittest.mock import mock_open, patch

import re
import pytest


@pytest.fixture
def path_to_match():
    return ["/from/here/i/cp", "/fsl/5.0/doc/fsl.css", ".files no_ext", "?.png"]


@pytest.fixture
def path_not_to_match():
    return [
        "5.0",
    ]


@pytest.fixture
def attr_to_match():
    return [
        " -p 2",
        " -p    98",
    ]


def test_match_paths(path_to_match, path_not_to_match):
    for s in path_to_match:
        assert re.match(INPUT_RE, s)

    for s in path_not_to_match:
        assert not re.match(INPUT_RE, s)


def test_match_attrs(attr_to_match):
    for s in attr_to_match:
        assert re.match(ATTRIBUTE_RE, s)


def test_readlines():
    # Test valid file
    m = mock_open(read_data="""<HTML><HEAD>
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
</pre></BODY></HTML>""")
    with patch("builtins.open", m, create=True):
        filename = "file.html"
        lines = readlines(filename)
        expected_output = {
            'Feat main script': [
                '/bin/cp /tmp/feat_oJmMLg.fsf design.fsf',
                '/usr/share/fsl-5.0/bin/feat_model design',
                'mkdir .files',
                'cp /usr/share/fsl-5.0/doc/fsl.css .files'
            ]
        }
        assert lines == expected_output

    # Test invalid file path
    with pytest.raises(FileNotFoundError):
        filename = "invalid_file.txt"
        lines = readlines(filename)


def test_get_entities():
    # positionnal argument
    df = {
        "name": "Command",
        "Used": [0],
        "GeneratedBy": [1]
    }
    cmd_s = ["Command", "arg_0", "arg_1"]
    expected_results = (['arg_0'], ['arg_1'], [])
    assert get_entities(cmd_s[1:], df) == expected_results

    # inputs, outputs : arg and kwarg
    df = {
        "name": "Command",
        "Used": [0, "-a"],
        "GeneratedBy": [1, "-b"]
    }
    cmd_s = ["Command", "arg_0", "arg_1", "-a", "kwarg_0",  "-b", "kwarg_1"]
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    expected_inputs = ["kwarg_0", "arg_0"]
    expected_outputs = ["kwarg_1", "arg_1"]
    expected_parameters = []
    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters

    # inputs, outputs : shuffle arg and kwarg
    df = {
        "name": "Command",
        "Used": [0, "-a"],
        "GeneratedBy": [1, "-b"]
    }
    cmd_s = ["Command", "-a", "kwarg_0", "arg_0", "arg_1",  "-b", "kwarg_1"]
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    expected_inputs = ["kwarg_0", "arg_0"]
    expected_outputs = ["kwarg_1", "arg_1"]
    expected_parameters = []
    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters

    # inputs, outputs : arg -1 and kwarg
    df = {
        "name": "Command",
        "Used": [0, "-a"],
        "GeneratedBy": [-1, "-b"]
    }
    cmd_s = ["Command", "-a", "kwarg_0", "arg_0", "arg_1",  "-b", "kwarg_1"]
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    expected_inputs = ["kwarg_0", "arg_0"]
    expected_outputs = ["kwarg_1", "arg_1"]
    expected_parameters = []
    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters

    # inputs, outputs : arg "0:-1" and kwarg
    df = {
        "name": "Command",
        "Used": ["0:-1", "-a"],
        "GeneratedBy": [-1, "-b"]
    }
    cmd_s = ["Command", "-a", "kwarg_0", "arg_0",
             "arg_1",  "-b", "kwarg_1", "arg_2"]
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    expected_inputs = ["kwarg_0", "arg_0", "arg_1"]
    expected_outputs = ["kwarg_1", "arg_2"]
    expected_parameters = []
    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters

    # inputs, outputs : arg and kwarg dict
    df = {
        "name": "Command",
        "Used": ["0:-1", "-a"],
        "GeneratedBy": [-1, "-b",  {
            "name": "-c",
            "index": ["0:2"]
        },
            {
            "name": "-d",
            "index": [3]
        },]
    }
    cmd_s = [
        "Command",
        "-a", "kwarg_0",
        "arg_0",
        "arg_1",
        "-b", "kwarg_1",
        "arg_2",
        "-c", "kwarg_2", "kwarg_3", "kwarg_4",
        "-d", "kwarg_5", "kwarg_6", "kwarg_7", "kwarg_8",
    ]
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    expected_inputs = ["kwarg_0", "arg_0", "arg_1"]
    expected_outputs = ["kwarg_1", "kwarg_2",
                        "kwarg_3", "kwarg_8", "arg_2"]
    expected_parameters = []

    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters

    # inputs, outputs, parameters : arg and kwarg, parameters
    df = {
        "name": "Command",
        "Used": [0, "-a"],
        "GeneratedBy": [-1, "-b"],
        "parameters_value": ["-c",
                             {
                                 "name": "-d",
                                 "index": ["0:2"]
                             }],
        "parameters_no_value": ["-e", "-f"]
    }
    cmd_s = [
        "Command",
        "-a", "kwarg_0",
        "arg_0",
        "arg_1",
        "-b", "kwarg_1",
        "arg_2",
        "-c", "kwarg_2",
        "-d", "kwarg_3", "kwarg_4", "kwarg_5", "kwarg_6",
    ]
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    expected_inputs = ["kwarg_0", "arg_0"]
    expected_outputs = ["kwarg_1", "arg_2"]
    expected_parameters = ["kwarg_2", "kwarg_3", "kwarg_4"]

    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters

    # inputs, outputs : arg and kwarg dict and nargs
    df = {
        "name": "Command",
        "Used": ["0:-1", "-a"],
        "GeneratedBy": [-1, "-b",  {
            "name": "-c",
            "index": ["0:2"],
            "nargs": 3,
        },
            {
            "name": "-d",
            "index": [3],
            "nargs": 5,
        },]
    }
    cmd_s = [
        "Command",
        "-a", "kwarg_0",
        "arg_0",
        "arg_1",
        "-b", "kwarg_1",
        "-c", "kwarg_2", "kwarg_3", "kwarg_4",
        "-d", "kwarg_5", "kwarg_6", "kwarg_7", "kwarg_8", "kwarg_9",
        "arg_2", "arg_3",
    ]
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)
    expected_inputs = ["kwarg_0", "arg_0", "arg_1", "arg_2"]
    expected_outputs = ["kwarg_1", "kwarg_2",
                        "kwarg_3", "kwarg_8", "arg_3"]
    expected_parameters = []

    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters


def test_get_entities_rm():
    df = {
        "name": "rm",
        "Used": ["0:"]
    }
    cmd = "/bin/rm -f sl?.png highres2standard2.png"
    cmd_s = cmd.split(" ")
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)

    expected_inputs = ["sl?.png", "highres2standard2.png"]
    expected_outputs = []
    expected_parameters = []

    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters


def test_get_entities_mv():
    df = {
        "name": "mv",
        "Used": ["0:-1"],
        "GeneratedBy": [-1]
    }
    cmd = "/bin/mv -f prefiltered_func_data_mcf.mat prefiltered_func_data_mcf.par prefiltered_func_data_mcf_abs.rms " \
          "prefiltered_func_data_mcf_abs_mean.rms prefiltered_func_data_mcf_rel.rms " \
          "prefiltered_func_data_mcf_rel_mean.rms mc"
    cmd_s = cmd.split(" ")
    inputs, outputs, parameters = get_entities(cmd_s[1:], df)

    expected_inputs = ["prefiltered_func_data_mcf.mat", "prefiltered_func_data_mcf.par",
                       "prefiltered_func_data_mcf_abs.rms", "prefiltered_func_data_mcf_abs_mean.rms",
                       "prefiltered_func_data_mcf_rel.rms", "prefiltered_func_data_mcf_rel_mean.rms"]
    expected_outputs = ["mc"]
    expected_parameters = []

    assert inputs == expected_inputs
    assert outputs == expected_outputs
    assert parameters == expected_parameters
