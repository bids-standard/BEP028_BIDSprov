import uuid
import random
import pytest
import os
import json
import hashlib

from bids_prov.utils import (
    get_uuid, get_random_string, get_rrid, make_alnum,
    get_activity_urn, get_agent_urn, get_entity_urn,
    get_default_graph, CONTEXT_URL, label_mapping, get_sha256
    )
from unittest.mock import mock_open, patch

def test_get_uuid():
    # Test that the function returns a valid UUID string
    result = get_uuid()
    assert isinstance(result, str)
    assert isinstance(uuid.UUID(result), uuid.UUID)

    # Test that the UUID returned is version 4
    assert uuid.UUID(result).version == 4

    # Test that the function returns a different ID each time it's called
    id1 = get_uuid()
    id2 = get_uuid()
    assert id1 != id2

def test_get_random_string():
    # Test that the function returns a random string
    result = get_random_string()
    assert isinstance(result, str)
    assert len(result) == 8
    assert result.isalnum()
    assert len(get_random_string(5)) == 5
    assert result != get_random_string()

def test_get_rrid():
    # Test that the function returns a RRID string
    result = get_rrid('FSL')
    assert 'RRID:' in result
    assert isinstance(result, str)
    assert result != get_rrid('SPM')

    # Test the the function returns None if the software is not referenced
    assert get_rrid('unreferenced_software') is None

def test_make_alnum():
    # Test that the function that removes all non alphanumeric chars from a string
    assert make_alnum('¨^$£$êµ*ad45@') == 'ad45'
    assert make_alnum('\\//:!§.;,?[]()}{}') == '' 
    assert make_alnum('ezeasdsa45ADA5sdas') == 'ezeasdsa45ADA5sdas'

def test_get_activity_urn():
    # Test that the function that returns URNs for activities
    assert 'urn:spm-' in get_activity_urn('SPM')
    assert len(get_activity_urn('SPM')) == 16
    assert 'urn:spmv1242-' in get_activity_urn('SPM v. 1242355')
    assert len(get_activity_urn('SPM v. 1242355')) == 21

def test_get_agent_urn():
    # Test that the function that returns URNs for agents
    assert 'urn:bet-' in get_agent_urn('BET')
    assert len(get_agent_urn('BET')) == 16
    assert 'urn:movefile-' in get_agent_urn('Move file')
    assert len(get_agent_urn('SPM v. 1242355')) == 21

def test_get_entity_urn():
    # Test that the function that returns URNs for entities
    assert get_entity_urn('') == 'bids::'
    assert get_entity_urn('sub-001/func/T1.nii') == 'bids::sub-001/func/T1.nii'
    assert get_entity_urn('T1.nii') == 'bids::T1.nii'

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
