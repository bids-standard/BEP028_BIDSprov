#!/usr/bin/python
# coding: utf-8

""" Tests for the bids_prov.merge module """

from os.path import abspath, join
import json
import unittest

from bids import BIDSLayout
from bids_prov.merge import (
    filter_provenance_group, get_provenance_files,
    get_described_datasets, get_described_files, get_described_sidecars,
    get_dataset_entity_record, get_entity_record, get_sidecar_entity_record,
    get_linked_entities, merge_records
    )

TEST_DATA_DIR = abspath(join('bids_prov', 'tests', 'samples_test'))
TEST_DATASET_0 = BIDSLayout(join(TEST_DATA_DIR, 'provenance_ds00'), is_derivative=True)
TEST_DATASET_1 = BIDSLayout(join(TEST_DATA_DIR, 'provenance_ds01'), is_derivative=True)
TEST_DATAFILE_1 = TEST_DATASET_1.get()[21]
TEST_DESCRIPTIONFILE_1 = TEST_DATASET_1.get()[0]
TEST_DATASET_2 = BIDSLayout(join(TEST_DATA_DIR, 'provenance_ds02'), is_derivative=False)
TEST_DATAFILE_2 = TEST_DATASET_2.get()[7]
TEST_DATASET_3 = BIDSLayout(join(TEST_DATA_DIR, 'provenance_ds03'), is_derivative=True)
TEST_DESCRIPTIONFILE_2 = TEST_DATASET_3.get()[0]

class TestMergeFunctions(unittest.TestCase):
    """ All tests for the bids_prov.merge module """

    def test_filter_provenance_group(self):
        """ Test the filter_provenance_group function """

        file_list = TEST_DATASET_1.get()
        assert not filter_provenance_group(file_list, 'dcm2niix')
        out_list = filter_provenance_group(file_list, 'spm')
        assert len(out_list) == 3
        assert out_list[0].filename == 'prov-spm_act.json'
        assert out_list[1].filename == 'prov-spm_ent.json'
        assert out_list[2].filename == 'prov-spm_soft.json'

        # Test dataset without provenance files
        file_list = TEST_DATASET_0.get()
        assert not filter_provenance_group(file_list, 'dcm2niix')
        assert not filter_provenance_group(file_list, 'bold')

    def test_get_provenance_files(self):
        """ Test the get_provenance_files function """

        assert not get_provenance_files(TEST_DATASET_0, 'env', 'spm')
        assert not get_provenance_files(TEST_DATASET_0, 'env')
        assert not get_provenance_files(TEST_DATASET_0, 'ent')
        assert not get_provenance_files(TEST_DATASET_0, 'act')
        assert not get_provenance_files(TEST_DATASET_0, 'soft')
        assert not get_provenance_files(TEST_DATASET_1, 'env', 'dcm2niix')
        assert not get_provenance_files(TEST_DATASET_1, 'env')
        assert not get_provenance_files(TEST_DATASET_1, 'env', 'spm')
        assert not get_provenance_files(TEST_DATASET_1, 'ent', 'dcm2niix')
        out_list = get_provenance_files(TEST_DATASET_1, 'ent')
        assert len(out_list) == 2
        assert out_list[0].relpath == join('prov', 'prov-preprocessing_ent.json')
        assert out_list[0].filename == 'prov-preprocessing_ent.json'
        assert out_list[1].relpath == join('prov', 'prov-spm_ent.json')
        assert out_list[1].filename == 'prov-spm_ent.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'ent', 'spm')
        assert len(out_list) == 1
        assert out_list[0].filename == 'prov-spm_ent.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'act')
        assert len(out_list) == 2
        assert out_list[0].relpath == join('prov', 'prov-preprocessing_act.json')
        assert out_list[0].filename == 'prov-preprocessing_act.json'
        assert out_list[1].relpath == join('prov', 'prov-spm_act.json')
        assert out_list[1].filename == 'prov-spm_act.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'act', 'spm')
        assert len(out_list) == 1
        assert out_list[0].filename == 'prov-spm_act.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'soft')
        assert len(out_list) == 2
        assert out_list[0].relpath == join('prov', 'prov-preprocessing_soft.json')
        assert out_list[0].filename == 'prov-preprocessing_soft.json'
        assert out_list[1].relpath == join('prov', 'prov-spm_soft.json')
        assert out_list[1].filename == 'prov-spm_soft.json'
        out_list = get_provenance_files(TEST_DATASET_1, 'soft', 'spm')
        assert len(out_list) == 1
        assert out_list[0].filename == 'prov-spm_soft.json'

    def test_get_described_datasets(self):
        """ Test the get_described_datasets function """

        assert not get_described_datasets(TEST_DATASET_0)

        described_datasets = get_described_datasets(TEST_DATASET_1)
        assert len(described_datasets) == 1
        assert described_datasets[0].relpath == 'dataset_description.json'
        assert described_datasets[0].filename == 'dataset_description.json'

        assert not get_described_datasets(TEST_DATASET_2)

        described_datasets = get_described_datasets(TEST_DATASET_3)
        assert len(described_datasets) == 1
        assert described_datasets[0].relpath == 'dataset_description.json'
        assert described_datasets[0].filename == 'dataset_description.json'

    def test_get_described_files(self):
        """ Test the get_described_files function """

        assert not get_described_files(TEST_DATASET_0)

        described_files = get_described_files(TEST_DATASET_1)
        assert len(described_files) == 17
        assert described_files[0].relpath == join('sub-01', 'anat', 'c1sub-01_T1w.nii')
        assert described_files[0].filename == 'c1sub-01_T1w.nii'
        assert described_files[4].relpath == join('sub-01', 'anat', 'c5sub-01_T1w.nii')
        assert described_files[4].filename == 'c5sub-01_T1w.nii'
        assert described_files[6].relpath == join('sub-01', 'anat', 'sub-01_T1w.nii')
        assert described_files[6].filename == 'sub-01_T1w.nii'

        described_files = get_described_files(TEST_DATASET_2)
        assert len(described_files) == 1
        assert described_files[0].relpath == join('sub-02', 'anat', 'sub-02_T1w.nii')
        assert described_files[0].filename == 'sub-02_T1w.nii'

        assert not get_described_files(TEST_DATASET_3)

    def test_get_described_sidecars(self):
        """ Test the get_described_sidecars function """

        assert not get_described_sidecars(TEST_DATASET_0)

        assert not get_described_sidecars(TEST_DATASET_1)

        described_sirecars = get_described_sidecars(TEST_DATASET_2)
        assert len(described_sirecars) == 1
        assert described_sirecars[0].relpath == join('sub-02', 'anat', 'sub-02_T1w.nii')
        assert described_sirecars[0].filename == 'sub-02_T1w.nii'

        assert not get_described_sidecars(TEST_DATASET_3)

    def test_get_dataset_entity_record(self):
        """ Test the get_dataset_entity_record function """

        entity = get_dataset_entity_record(TEST_DESCRIPTIONFILE_1)
        assert entity == {
            'Id': 'bids:current_dataset',
            'Label': 'Provenance records for SPM-based fMRI statistical analysis',
            'GeneratedBy': ['bids::prov#preprocessing-yBHdvts7']
            }

        entity = get_dataset_entity_record(TEST_DESCRIPTIONFILE_2)
        assert entity == {
            'Id': 'bids:current_dataset',
            'Label': 'Outputs from fMRIPrep preprocessing',
            'GeneratedBy': ['bids::prov#preprocessing-xMpFqB5q']
            }

    def test_get_entity_record(self):
        """ Test the get_entity_record function """

        entity = get_entity_record(TEST_DATASET_1, TEST_DATAFILE_1)
        assert entity == {
            'Id': 'bids::sub-01/anat/sub-01_T1w.nii',
            'Label': 'sub-01_T1w.nii',
            'AtLocation': join('sub-01', 'anat', 'sub-01_T1w.nii'),
            'GeneratedBy': 'bids::prov#coregister-6d38be4a',
            'Digest':
                {
                    'sha256': 'f29cb68cce4cb3aa2ccbc791aceff3705a23e07dfc40c045a7ce3879ebc1f338'
                }
        }

        entity = get_entity_record(TEST_DATASET_2, TEST_DATAFILE_2)
        assert entity == {
            'Id': 'bids::sub-02/anat/sub-02_T1w.nii',
            'Label': 'sub-02_T1w.nii',
            'AtLocation': join('sub-02', 'anat', 'sub-02_T1w.nii'),
            'GeneratedBy': 'bids::prov#conversion-00f3a18f'
            }

    def test_get_sidecar_entity_record(self):
        """ Test the get_sidecar_entity_record function """

        entity = get_sidecar_entity_record(TEST_DATASET_2, TEST_DATAFILE_2)
        assert entity == {
            'Id': 'bids::sub-02/anat/sub-02_T1w.json',
            'Label': 'sub-02_T1w.json',
            'AtLocation': join('sub-02', 'anat', 'sub-02_T1w.json'),
            'GeneratedBy': 'bids::prov#conversion-00f3a18f'
            }

    def test_get_linked_entities(self):
        """ Test the get_linked_entities function """

        with open(join(TEST_DATA_DIR, 'test_linked_entities.jsonld'),
            encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            linked_entities = get_linked_entities(json_contents)
            assert len(linked_entities) == 2
            for entity_id in ['urn:not_used', 'urn:not_generated']:
                assert entity_id in linked_entities

    def test_merge_records(self):
        """ Test the merge_records function """

        # Tests for groups that are not present
        assert merge_records(TEST_DATASET_1, 'fake_group') == {
            '@context': 'https://purl.org/nidash/bidsprov/context.json',
            'BIDSProvVersion': '0.0.1',
            'Records': {
                'Activities': [],
                'Entities': [],
                'Software': []
                }
            }

        # Tests for all groups in the dataset
        with open(join(TEST_DATA_DIR, 'provenance_ds01.jsonld'), encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            assert merge_records(TEST_DATASET_1) == json_contents

        # Tests for specific groups in the dataset
        with open(
            join(TEST_DATA_DIR, 'provenance_ds01_spm.jsonld'), encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            assert merge_records(TEST_DATASET_1, 'spm') == json_contents

        with open(join(TEST_DATA_DIR, 'provenance_ds01_preprocessing.jsonld'),
            encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            assert merge_records(TEST_DATASET_1, 'preprocessing') == json_contents

        with open(join(TEST_DATA_DIR, 'provenance_ds02.jsonld'),encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            print(json.dumps(merge_records(TEST_DATASET_2), indent=2))
            assert merge_records(TEST_DATASET_2) == json_contents
            assert merge_records(TEST_DATASET_2, 'dcm2niix') == json_contents

        with open(join(TEST_DATA_DIR, 'provenance_ds03.jsonld'), encoding = 'utf-8') as test_file:
            json_contents = json.load(test_file)
            assert merge_records(TEST_DATASET_3) == json_contents
            assert merge_records(TEST_DATASET_3, 'fmriprep') == json_contents

if __name__ == '__main__':
    unittest.main()
