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
    parameters = [1, 3, "-b"]
    expected_output = ['input1', 'input2', 'input2']
    assert get_entities(cmd_s, parameters) == expected_output

    cmd_s = ["command", "input1", "-b", "input2"]
    parameters = [0, 1, "-b"]
    expected_output = ['command', 'input1', 'input2']
    assert get_entities(cmd_s, parameters) == expected_output

    cmd_s = ["command", "-a", "input1", "-b", "input2"]
    parameters = ["-a", "-b"]
    expected_output = ['input1', 'input2']
    assert get_entities(cmd_s, parameters) == expected_output



