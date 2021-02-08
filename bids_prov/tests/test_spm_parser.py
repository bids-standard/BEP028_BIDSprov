import pytest
import json

from ..spm_parser import get_records


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
