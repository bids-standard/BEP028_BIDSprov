from ..fsl_parser import INPUT_RE, ATTRIBUTE_RE, readlines
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
        "-p 2",
        "-p    98",
    ]


def test_match_paths(path_to_match, path_not_to_match):
    for s in path_to_match:
        assert re.match(INPUT_RE, s)

    for s in path_not_to_match:
        assert not re.match(INPUT_RE, s)


def test_match_attrs(attr_to_match):
    for s in attr_to_match:
        assert re.match(ATTRIBUTE_RE, s)


from collections import defaultdict
from unittest.mock import mock_open, patch
import pytest


def test_readlines():
    # Test valid file
    m = mock_open(read_data="""#### Feat main script

/bin/cp /tmp/feat_oJmMLg.fsf design.fsf
/usr/share/fsl/5.0/bin/feat_model design
mkdir .files;cp /usr/share/fsl/5.0/doc/fsl.css .files""")
    with patch("builtins.open", m, create=True):
        filename = "file.txt"
        lines = readlines(filename)
        expected_output = {
            'Feat main script': [
                '/bin/cp /tmp/feat_oJmMLg.fsf design.fsf',
                '/usr/share/fsl/5.0/bin/feat_model design',
                'mkdir .files',
                'cp /usr/share/fsl/5.0/doc/fsl.css .files'
            ]
        }
        assert lines == expected_output

    # Test invalid file path
    with pytest.raises(FileNotFoundError):
        filename = "invalid_file.txt"
        lines = readlines(filename)



