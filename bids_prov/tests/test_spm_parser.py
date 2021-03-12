import pytest
import json

from ..spm_config import DEPENDENCY_REGEX
from ..spm_parser import get_records, get_closest_activity
import re


def test_get_records_copy_attributes():
    task_groups = dict(
        file_ops_1=[
            ".files = {'$PATH-TO-NII-FILES/tonecounting_bold.nii.gz'};",
            ".action.copyto = {'$PATH-TO-PREPROCESSING/FUNCTIONAL'};",
        ]
    )
    recs = get_records(task_groups)
    attrs = [_["attributes"] for _ in recs["prov:Activity"]]
    assert "action.copyto" in json.dumps(attrs)


def test_get_records_attrs():
    task_groups = dict(
        estwrite_5=[
            ".sep = 4;",
            ".fwhm = 5;",
        ]
    )
    recs = get_records(task_groups)
    attrs = [_["attributes"] for _ in recs["prov:Activity"]]
    assert "4" in json.dumps(attrs)


def test_dep_regex():
    s = """
    cfg_dep('Normalise: Write: Normalised Images (Subj 1)', 
    substruct('.','val', '{}',{8}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', 
    '{}',{1}), substruct('()',{1}, '.','files'));
    """
    assert re.search(DEPENDENCY_REGEX, s, re.IGNORECASE) is not None


def test_closest_activity():
    records = {
        "prov:Activity": [
            {"@id": "niiri:cfg_basicio.file_dir.file_ops.file_move._1kuxDmvbfxp"},
            {"@id": "niiri:cfg_basicio.file_dir.file_ops.file_move._1kuxDmvbfxp"},
        ]
    }
