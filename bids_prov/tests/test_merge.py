#!/usr/bin/python
# coding: utf-8

""" Tests for the bids_prov.merge module """

""" Test data:
- dataset level provenance description
- file level provenance description + prov/
- several provenance groups
"""

from os.path import abspath, join
import json
import unittest

from bids import BIDSLayout
from bids.layout.models import BIDSJSONFile, BIDSFile
from bids_prov.merge import (
    filter_provenance_group, get_provenance_files,
    get_described_datasets, get_described_files, get_described_sidecars,
    get_dataset_entity_record, get_entity_record, get_sidecar_entity_record,
    merge_records
    )

TEST_DATA_DIR = abspath(join('bids_prov', 'tests', 'samples_test'))
TEST_DATASET_1 = BIDSLayout(join(TEST_DATA_DIR, 'provenance_ds01'))
TEST_DATAFILE_1 = TEST_DATASET_1.get()[6]
TEST_DATASET_2 = BIDSLayout(join(TEST_DATA_DIR, 'provenance_ds02'))
TEST_DATAFILE_2 = TEST_DATASET_2.get()[7]
TEST_DATASET_3 = BIDSLayout(join(TEST_DATA_DIR, 'provenance_ds03'))
TEST_DESCRIPTIONFILE_1 = TEST_DATASET_3.get()[0]

class TestMergeFunctions(unittest.TestCase):

    def test_filter_provenance_group(self):
        """ Test the filter_provenance_group function """

        file_list = TEST_DATASET_1.get()
        assert filter_provenance_group(file_list, 'dcm2niix') == []
        out_list = filter_provenance_group(file_list, 'spm')
        assert len(out_list) == 3
        assert out_list[0].filename == 'prov-spm_act.json'
        assert out_list[1].filename == 'prov-spm_ent.json'
        assert out_list[2].filename == 'prov-spm_soft.json'

        # TODO -> test dataset without provenance files

    def test_get_provenance_files(self):
        """ Test the get_provenance_files function """

        assert get_provenance_files(TEST_DATASET_1, 'env', 'dcm2niix') == []
        assert get_provenance_files(TEST_DATASET_1, 'env') == []
        assert get_provenance_files(TEST_DATASET_1, 'env', 'spm') == []
        assert get_provenance_files(TEST_DATASET_1, 'ent', 'dcm2niix') == []
        out_list = get_provenance_files(TEST_DATASET_1, 'ent')
        assert len(out_list) == 1
        assert out_list[0].relpath == join('prov', 'prov-spm_ent.json')
        assert out_list[0].filename == 'prov-spm_ent.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'ent', 'spm')
        assert len(out_list) == 1
        assert out_list[0].filename == 'prov-spm_ent.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'act')
        assert len(out_list) == 1
        assert out_list[0].relpath == join('prov', 'prov-spm_act.json')
        assert out_list[0].filename == 'prov-spm_act.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'act', 'spm')
        assert len(out_list) == 1
        assert out_list[0].filename == 'prov-spm_act.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'soft')
        assert len(out_list) == 1
        assert out_list[0].relpath == join('prov', 'prov-spm_soft.json')
        assert out_list[0].filename == 'prov-spm_soft.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'soft', 'spm')
        assert len(out_list) == 1
        assert out_list[0].filename == 'prov-spm_soft.json'

        # TODO -> test dataset without provenance files

    def test_get_described_datasets(self):
        """ Test the get_described_datasets function """

        assert get_described_datasets(TEST_DATASET_1) == []
        assert get_described_datasets(TEST_DATASET_2) == []

        described_datasets = get_described_datasets(TEST_DATASET_3)
        assert len(described_datasets) == 1
        assert described_datasets[0].relpath == 'dataset_description.json'
        assert described_datasets[0].filename == 'dataset_description.json'

    def test_get_described_files(self):
        """ Test the get_described_files function """

        described_files = get_described_files(TEST_DATASET_1)
        assert len(described_files) == 1
        assert described_files[0].relpath == join('sub-01', 'anat', 'sub-01_T1w.nii')
        assert described_files[0].filename == 'sub-01_T1w.nii'

        described_files = get_described_files(TEST_DATASET_2)
        assert len(described_files) == 1
        assert described_files[0].relpath == join('sub-02', 'anat', 'sub-02_T1w.nii')
        assert described_files[0].filename == 'sub-02_T1w.nii'

        assert get_described_files(TEST_DATASET_3) == []

    def test_get_described_sidecars(self):
        """ Test the get_described_sidecars function """

        assert get_described_sidecars(TEST_DATASET_1) == []

        described_sirecars = get_described_sidecars(TEST_DATASET_2)
        assert len(described_sirecars) == 1
        assert described_sirecars[0].relpath == join('sub-02', 'anat', 'sub-02_T1w.nii')
        assert described_sirecars[0].filename == 'sub-02_T1w.nii'

        assert get_described_sidecars(TEST_DATASET_3) == []
        
    def test_get_dataset_entity_record(self):
        """ Test the get_dataset_entity_record function """
        
        entity = get_dataset_entity_record(TEST_DESCRIPTIONFILE_1)
        assert entity == {
            'Id': 'bids:current_dataset',
            'Label': 'Outputs from fMRIPrep preprocessing',
            'AtLocation': join(TEST_DATA_DIR, 'provenance_ds03'),
            'GeneratedBy': ['bids::prov#preprocessing-xMpFqB5q']
            }

    def test_get_entity_record(self):
        """ Test the get_entity_record function """

        entity = get_entity_record(TEST_DATAFILE_1)
        assert entity == {
            'Id': 'bids::sub-01/anat/sub-01_T1w.nii',
            'Label': 'sub-01_T1w.nii',
            'AtLocation': join(TEST_DATA_DIR, 'provenance_ds01', 'sub-01', 'anat', 'sub-01_T1w.nii'),
            'GeneratedBy': 'bids::prov/#coregister-6d38be4a',
            'Digest':
                {
                    'sha256': 'f29cb68cce4cb3aa2ccbc791aceff3705a23e07dfc40c045a7ce3879ebc1f338'
                }
        }

        entity = get_entity_record(TEST_DATAFILE_2)
        assert entity == {
            'Id': 'bids::sub-02/anat/sub-02_T1w.nii',
            'Label': 'sub-02_T1w.nii',
            'AtLocation': join(TEST_DATA_DIR, 'provenance_ds02', 'sub-02', 'anat', 'sub-02_T1w.nii'),
            'GeneratedBy': 'bids::prov/#conversion-00f3a18f'
            }

    def test_get_sidecar_entity_record(self):
        """ Test the get_sidecar_entity_record function """

        entity = get_sidecar_entity_record(TEST_DATAFILE_2)
        assert entity == {
            'Id': 'bids::sub-02/anat/sub-02_T1w.json',
            'Label': 'sub-02_T1w.json',
            'AtLocation': join(TEST_DATA_DIR, 'provenance_ds02', 'sub-02', 'anat', 'sub-02_T1w.json'),
            'GeneratedBy': 'bids::prov/#conversion-00f3a18f'
            }

    def test_merge_records(self):
        """ Test the merge_records function """

        with open(join(TEST_DATA_DIR, 'provenance_ds01.jsonld'), encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            assert merge_records(TEST_DATASET_1) == json_contents
            assert merge_records(TEST_DATASET_1, 'spm') == json_contents

        with open(join(TEST_DATA_DIR, 'provenance_ds02.jsonld'), encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            assert merge_records(TEST_DATASET_2) == json_contents
            assert merge_records(TEST_DATASET_2, 'dcm2niix') == json_contents

        with open(join(TEST_DATA_DIR, 'provenance_ds03.jsonld'), encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            assert merge_records(TEST_DATASET_3) == json_contents
            assert merge_records(TEST_DATASET_3, 'fmriprep') == json_contents

        # TODO : tests for groups that are not present
        # TODO : check test_files

if __name__ == '__main__':
    unittest.main()
