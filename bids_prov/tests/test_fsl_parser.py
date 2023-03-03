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
    cmd_s = ["command", "-a", "input1", "-b", "input2"]
    parameters = ["-a", 4, "-b"]
    expected_output = ['input1', 'input2', 'input2']
    entities, args_consumed_list =  get_entities(cmd_s, parameters)
    assert entities == expected_output


    cmd_s = ["command", "input1", "-b", "input2"]
    parameters = [0, 1, "-b"]
    expected_output = ['command', 'input1', 'input2']
    entities, args_consumed_list =  get_entities(cmd_s, parameters)

    assert entities == expected_output

    cmd_s = ["command", "-a", "input1", "-b", "input2"]
    parameters = [1]
    expected_output = []
    entities, args_consumed_list =  get_entities(cmd_s, parameters)

    assert entities == expected_output


def test_get_entities_rm():
    cmd = "/bin/rm -f sl?.png highres2standard2.png"
    cmd_s = cmd.split(" ")
    parameters = ["1:"]
    expected_output = ["sl?.png", "highres2standard2.png"]
    entities, args_consumed_list =  get_entities(cmd_s, parameters)
    assert entities == expected_output


def test_get_entities_mv():
    cmd = "/bin/mv -f prefiltered_func_data_mcf.mat prefiltered_func_data_mcf.par prefiltered_func_data_mcf_abs.rms " \
          "prefiltered_func_data_mcf_abs_mean.rms prefiltered_func_data_mcf_rel.rms " \
          "prefiltered_func_data_mcf_rel_mean.rms mc"
    cmd_s = cmd.split(" ")
    parameters = ["1:-1"]
    expected_inputs = ["prefiltered_func_data_mcf.mat", "prefiltered_func_data_mcf.par",
                       "prefiltered_func_data_mcf_abs.rms", "prefiltered_func_data_mcf_abs_mean.rms",
                       "prefiltered_func_data_mcf_rel.rms", "prefiltered_func_data_mcf_rel_mean.rms"]
    entities, args_consumed_list =  get_entities(cmd_s, parameters)
    assert entities== expected_inputs

    parameters = [-1]
    expected_outputs = ["mc"]
    entities, args_consumed_list =  get_entities(cmd_s, parameters)
    assert entities == expected_outputs


def test_get_entities_dict():
    cmd = "/slicer example_func2highres highres -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png"
    cmd_s = cmd.split(" ")
    parameters = [{"name": "-x", "index": 2}]
    expected_outputs = ["sla.png", "slb.png", "slc.png"]
    assert get_entities(cmd_s, parameters)[0] == expected_outputs


