import uuid
import random
import pytest
import os
import json
import hashlib

from bids_prov.utils import (
    get_id, get_rrid, get_default_graph, CONTEXT_URL, label_mapping, get_sha256
    )
from unittest.mock import mock_open, patch


def test_get_id():
    # Test that the function returns a valid UUID string
    result = get_id()
    assert isinstance(result, str)
    assert isinstance(uuid.UUID(result), uuid.UUID)

    # Test that the UUID returned is version 4
    assert uuid.UUID(result).version == 4

    # Test that the function returns a different ID each time it's called
    id1 = get_id()
    id2 = get_id()
    assert id1 != id2

def test_get_rrid():
    # Test that the function returns a RRID string
    result = get_rrid('FSL')
    assert 'RRID:' in result
    assert isinstance(result, str)
    assert result != get_rrid('SPM')

    # Test the the function returns None if the software is not referenced
    assert get_rrid('unreferenced_software') is None

def test_get_default_graph():
    context_url = "http://example.com/context"
    spm_ver = "v1.0"

    # Test the default arguments
    label = 'SPM'
    graph, agent_id = get_default_graph(label)
    assert graph["@context"] == CONTEXT_URL
    assert graph["Records"]["Software"][0]["Label"] == label
    assert graph["Records"]["Software"][0]["AltIdentifier"] == 'RRID:SCR_007037'
    assert agent_id is not None

    # Test custom arguments
    label = 'Nipype'
    graph, agent_id = get_default_graph('Nipype', spm_ver, context_url)
    assert graph["@context"] == context_url
    assert graph["Records"]["Software"][0]["Label"] == label
    assert graph["Records"]["Software"][0]["Version"] == spm_ver
    assert 'AltIdentifier' not in graph["Records"]["Software"][0]
    assert agent_id is not None

def test_label_mapping():
    label = "label1"
    mapping_json = {"label1": "mapped_label1", "label2": "mapped_label2"}
    filedir = os.path.dirname(__file__)
    filepath = os.path.join(filedir, "mapping_labels/", "mapping.json")
    m = mock_open(read_data=json.dumps(mapping_json))
    with patch("builtins.open", m, create=True):
        # Test label present in the mapping file
        mapped_label = label_mapping(label, filepath)
        assert mapped_label == "mapped_label1"

        # Test label not present in the mapping file
        label = "label3"
        mapped_label = label_mapping(label, filepath)
        assert mapped_label == "label3"


def test_get_sha256():
    # Test file with valid content
    m = mock_open(read_data=b"valid content")
    with patch("builtins.open", m, create=True):
        file_path = "file.txt"
        sha256 = get_sha256(file_path)
        assert sha256 == hashlib.sha256(b"valid content").hexdigest()

    # Test empty file
    m = mock_open(read_data=b"")
    with patch("builtins.open", m, create=True):
        file_path = "file.txt"
        sha256 = get_sha256(file_path)
        assert sha256 == hashlib.sha256(b"").hexdigest()

    # Test invalid file path
    with pytest.raises(FileNotFoundError):
        file_path = "invalid_file.txt"
        sha256 = get_sha256(file_path)

    # Test empty file path
    with pytest.raises(FileNotFoundError):
        file_path = ""
        sha256 = get_sha256(file_path)
