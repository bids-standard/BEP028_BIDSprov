from ..fsl_parser import INPUT_RE, ATTRIBUTE_RE, format_label
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


# TODO : attributes


def test_format_label():
    assert format_label("/path/to/somewhere.txt") == format_label("somewhere.txt")
