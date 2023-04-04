import json
import os
import random
import re
import uuid

import rdflib
from deepdiff import DeepDiff

from bids_prov.spm.spm_config import has_parameter, DEPENDENCY_REGEX
from bids_prov.spm.spm_parser import get_records, group_lines, get_input_entity, format_activity_name, spm_to_bids_prov
from bids_prov.utils import CONTEXT_URL
from .compare_graph import load_jsonld11_for_rdf, is_included_rdf_graph

random.seed(14)  # Control random generation for test, init at each import
INIT_STATE = random.getstate()


def init_random_state():  # force init to initial state
    random.setstate(INIT_STATE)


def test_spm_to_bids_prov(verbose=False):
    """
    Test if {batch_name}_ref.jsonld (which has been defined in advance) is included in the result of the input file parser
    {batch_name}.m

    batch file name.m  and reference name_ref.jsonld should be present in BEP028_BIDSprov/bids_prov/tests/samples_test
    """

    random.seed(14)  # Control random generation for test, init at each import
    INIT_STATE = random.getstate()

    dir_sample_test = os.path.abspath('./bids_prov/tests/samples_test')
    if verbose:
        print('\n-> SEED init state[0]', INIT_STATE[0])
        print("\n test_spm_to_bids_prov: Compare .m to a reference jsonld in directory:\n", dir_sample_test)

    all_files = os.listdir(dir_sample_test)
    sample_spm_list = [f for f in all_files if os.path.splitext(f)[-1] == '.m']

    for idx, sample_spm in enumerate(sample_spm_list):
        init_random_state()  # random seed initialisation for each batch.m
        name = os.path.splitext(sample_spm)[0]
        ref_jsonld = os.path.join(dir_sample_test, name + '_ref.jsonld')

        if os.path.exists(ref_jsonld):
            if verbose:
                print(f"TEST n°{idx}: {name}.m // reference {name}_ref.jsonld")
            new_jsonld = os.path.join(dir_sample_test, name + '.jsonld')
            spm_batch = os.path.join(dir_sample_test, sample_spm)
            spm_to_bids_prov(spm_batch, CONTEXT_URL, output_file=new_jsonld)

            jsonld11_ref = load_jsonld11_for_rdf(ref_jsonld, pyld_convert=True)
            # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
            graph_ref = rdflib.ConjunctiveGraph()
            graph_ref.parse(data=json.dumps(jsonld11_ref, indent=2), format='json-ld')

            jsonld11_new = load_jsonld11_for_rdf(new_jsonld, pyld_convert=True)
            graph_new = rdflib.ConjunctiveGraph()
            graph_new.parse(data=json.dumps(jsonld11_new, indent=2), format='json-ld')

            res_compare = is_included_rdf_graph(graph_ref, graph_new, verbose=verbose)

            if verbose:
                print(f"TEST n°{idx}: {name}.m // reference {name}_ref.jsonld -> {res_compare}")

            assert res_compare

        if verbose and not os.path.exists(ref_jsonld):
            print(f"TEST n°{idx}: reference {name}_ref.jsonld not found")


def test_group_lines():
    group = group_lines(LIST_READLINES)
    assert DeepDiff(group, TASKS) == {}


def test_format_activity_name():
    s = "cfg_basicio.file_dir.file_ops.file_move._1"
    assert format_activity_name(s) == 'Move file._1'
    s = "spm.cfg_basicio.file_dir.file_ops.file_move._1"
    assert format_activity_name(s) == 'Move file._1'


def test_get_input_entity():
    left = "files"
    right = "{'ds011/sub-01/func/sub-01_task-tonecounting_bold_trunctest.nii.gz'};"
    # entity label : sub-01_task-tonecounting_bold.nii.gz
    entities = [{
        "@id": "urn:c15521b1-b3dc-450a-9daa-37e51b591d75",
        "label": "func_sub-01_task-tonecounting_bold_trunctest.nii.gz",
        "prov:atLocation": "ds011/sub-01/func/sub-01_task-tonecounting_bold_trunctest.nii.gz"
    }]
    init_random_state()
    right_entity = get_input_entity(right)[0]
    assert right_entity == entities[0]


def test_has_parameter():
    string = "files"
    assert not has_parameter(string)  # == False

    string = "file_dir.file_ops.file_move._2"
    assert not has_parameter(string)

    string = "channel.vols(1)"
    assert has_parameter(string)

    string = "consess{1}.tcon.name"
    assert not has_parameter(string)


def test_get_records_copy_attributes():
    task_groups = dict(file_ops_1=[".files = {'$PATH-TO-NII-FILES/tonecounting_bold.nii.gz'};",
                                   ".action.copyto = {'$PATH-TO-PREPROCESSING/FUNCTIONAL'};",
                                   ]
                       )
    recs = get_records(task_groups, str(uuid.uuid4()))
    attrs = [activity["parameters"] for activity in recs["prov:Activity"]]
    assert "action.copyto" in json.dumps(attrs)


def test_get_records_attrs():
    task_groups = dict(estwrite_5=[".sep = 4;",
                                   ".fwhm = 5;", ]
                       )
    recs = get_records(task_groups, "agentUUID")
    attrs = [activity["parameters"] for activity in recs["prov:Activity"]]
    assert "4" in json.dumps(attrs)


def test_dep_regex():
    s = """
    cfg_dep('Normalise: Write: Normalised Images (Subj 1)', 
    substruct('.','val', '{}',{8}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', 
    '{}',{1}), substruct('()',{1}, '.','files'));
    """
    assert re.search(DEPENDENCY_REGEX, s, re.IGNORECASE) is not None


LIST_READLINES = [
    "matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_move.files = {'$HOME/nidmresults-examples/spm_default/ds011/sub-01/func/sub-01_task-tonecounting_bold.nii.gz'};",
    "matlabbatch{1}.cfg_basicio.file_dir.file_ops.file_move.action.copyto = {'$HOME/nidmresults-examples/spm_default/ds011/PREPROCESSING/FUNCTIONAL'};",
    "matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_move.files = {'/home/remiadon/nidmresults-examples/spm_default/ds011/sub-01/anat/sub-01_T1w.nii.gz'};",
    "matlabbatch{2}.cfg_basicio.file_dir.file_ops.file_move.action.copyto = {'/home/remiadon/nidmresults-examples/spm_default/ds011/PREPROCESSING/ANATOMICAL'};",
    "matlabbatch{3}.cfg_basicio.file_dir.file_ops.cfg_gunzip_files.files(1) = cfg_dep('Move/Delete Files: Moved/Copied Files', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));",
    "matlabbatch{4}.cfg_basicio.file_dir.file_ops.cfg_gunzip_files.files(1) = cfg_dep('Move/Delete Files: Moved/Copied Files', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));",
    "matlabbatch{5}.spm.spatial.realign.estwrite.data{1}(1) = cfg_dep('GunZip Files: GunZipped Files', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{':'}));",
    "matlabbatch{5}.spm.spatial.realign.estwrite.eoptions.quality = 0.9;",
    "matlabbatch{5}.spm.spatial.realign.estwrite.eoptions.sep = 4;",
    "matlabbatch{5}.spm.spatial.realign.estwrite.eoptions.fwhm = 5;",
    "matlabbatch{5}.spm.spatial.realign.estwrite.eoptions.rtm = 1;",
    "matlabbatch{5}.spm.spatial.realign.estwrite.eoptions.interp = 2;",
    "matlabbatch{5}.spm.spatial.realign.estwrite.eoptions.wrap = [0 0 0];",
    "matlabbatch{5}.spm.spatial.realign.estwrite.eoptions.weight = '';",
    "matlabbatch{5}.spm.spatial.realign.estwrite.roptions.which = [0 1];",
    "matlabbatch{5}.spm.spatial.realign.estwrite.roptions.interp = 4;",
    "matlabbatch{5}.spm.spatial.realign.estwrite.roptions.wrap = [0 0 0];",
    "matlabbatch{5}.spm.spatial.realign.estwrite.roptions.mask = 1;",
    "matlabbatch{5}.spm.spatial.realign.estwrite.roptions.prefix = 'r';",
    "matlabbatch{6}.spm.spatial.coreg.estimate.ref(1) = cfg_dep('Realign: Estimate & Reslice: Mean Image', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','rmean'));",
    "matlabbatch{6}.spm.spatial.coreg.estimate.source(1) = cfg_dep('GunZip Files: GunZipped Files', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{':'}));",
    "matlabbatch{6}.spm.spatial.coreg.estimate.other = {''};",
    "matlabbatch{6}.spm.spatial.coreg.estimate.eoptions.cost_fun = 'nmi';",
    "matlabbatch{6}.spm.spatial.coreg.estimate.eoptions.sep = [4 2];",
    "matlabbatch{6}.spm.spatial.coreg.estimate.eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];",
    "matlabbatch{6}.spm.spatial.coreg.estimate.eoptions.fwhm = [7 7];",
    "matlabbatch{7}.spm.spatial.preproc.channel.vols(1) = cfg_dep('GunZip Files: GunZipped Files', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{':'}));",
    "matlabbatch{7}.spm.spatial.preproc.channel.biasreg = 0.001;",
    "matlabbatch{7}.spm.spatial.preproc.channel.biasfwhm = 60;",
    "matlabbatch{7}.spm.spatial.preproc.channel.write = [0 1];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(1).tpm = {'/home/radon/spm12/tpm/TPM.nii,1'};",
    "matlabbatch{7}.spm.spatial.preproc.tissue(1).ngaus = 1;",
    "matlabbatch{7}.spm.spatial.preproc.tissue(1).native = [1 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(1).warped = [0 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(2).tpm = {'/home/radon/spm12/tpm/TPM.nii,2'};",
    "matlabbatch{7}.spm.spatial.preproc.tissue(2).ngaus = 1;",
    "matlabbatch{7}.spm.spatial.preproc.tissue(2).native = [1 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(2).warped = [0 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(3).tpm = {'/home/radon/spm12/tpm/TPM.nii,3'};",
    "matlabbatch{7}.spm.spatial.preproc.tissue(3).ngaus = 2;",
    "matlabbatch{7}.spm.spatial.preproc.tissue(3).native = [1 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(3).warped = [0 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(4).tpm = {'/home/radon/spm12/tpm/TPM.nii,4'};",
    "matlabbatch{7}.spm.spatial.preproc.tissue(4).ngaus = 3;",
    "matlabbatch{7}.spm.spatial.preproc.tissue(4).native = [1 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(4).warped = [0 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(5).tpm = {'/home/radon/spm12/tpm/TPM.nii,5'};",
    "matlabbatch{7}.spm.spatial.preproc.tissue(5).ngaus = 4;",
    "matlabbatch{7}.spm.spatial.preproc.tissue(5).native = [1 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(5).warped = [0 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(6).tpm = {'/home/radon/spm12/tpm/TPM.nii,6'};",
    "matlabbatch{7}.spm.spatial.preproc.tissue(6).ngaus = 2;",
    "matlabbatch{7}.spm.spatial.preproc.tissue(6).native = [0 0];",
    "matlabbatch{7}.spm.spatial.preproc.tissue(6).warped = [0 0];",
    "matlabbatch{7}.spm.spatial.preproc.warp.mrf = 1;",
    "matlabbatch{7}.spm.spatial.preproc.warp.cleanup = 1;",
    "matlabbatch{7}.spm.spatial.preproc.warp.reg = [0 0.001 0.5 0.05 0.2];",
    "matlabbatch{7}.spm.spatial.preproc.warp.affreg = 'mni';",
    "matlabbatch{7}.spm.spatial.preproc.warp.fwhm = 0;",
    "matlabbatch{7}.spm.spatial.preproc.warp.samp = 3;",
    "matlabbatch{7}.spm.spatial.preproc.warp.write = [0 1];",
    "matlabbatch{8}.spm.spatial.normalise.write.subj.def(1) = cfg_dep('Segment: Forward Deformations', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','fordef', '()',{':'}));",
    "matlabbatch{8}.spm.spatial.normalise.write.subj.resample(1) = cfg_dep('Realign: Estimate & Reslice: Realigned Images (Sess 1)', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','sess', '()',{1}, '.','cfiles'));",
    "matlabbatch{8}.spm.spatial.normalise.write.woptions.bb = [-78 -112 -70 78 76 85];",
    "matlabbatch{8}.spm.spatial.normalise.write.woptions.vox = [2 2 2];",
    "matlabbatch{8}.spm.spatial.normalise.write.woptions.interp = 4;",
    "matlabbatch{8}.spm.spatial.normalise.write.woptions.prefix = 'w';",
    "matlabbatch{9}.spm.spatial.normalise.write.subj.def(1) = cfg_dep('Segment: Forward Deformations', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','fordef', '()',{':'}));",
    "matlabbatch{9}.spm.spatial.normalise.write.subj.resample(1) = cfg_dep('Segment: Bias Corrected (1)', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','channel', '()',{1}, '.','biascorr', '()',{':'}));",
    "matlabbatch{9}.spm.spatial.normalise.write.woptions.bb = [-78 -112 -70 78 76 85];",
    "matlabbatch{9}.spm.spatial.normalise.write.woptions.vox = [2 2 2];",
    "matlabbatch{9}.spm.spatial.normalise.write.woptions.interp = 4;",
    "matlabbatch{9}.spm.spatial.normalise.write.woptions.prefix = 'w';",
    "matlabbatch{10}.spm.spatial.smooth.data(1) = cfg_dep('Normalise: Write: Normalised Images (Subj 1)', substruct('.','val', '{}',{8}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{1}, '.','files'));",
    "matlabbatch{10}.spm.spatial.smooth.fwhm = [6 6 6];",
    "matlabbatch{10}.spm.spatial.smooth.dtype = 0;",
    "matlabbatch{10}.spm.spatial.smooth.im = 0;",
    "matlabbatch{10}.spm.spatial.smooth.prefix = 's';",
    "matlabbatch{11}.spm.stats.fmri_spec.dir = {'/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/TEST/nidmresults-examples/spm_voxelwise_p0001'};",
    "matlabbatch{11}.spm.stats.fmri_spec.timing.units = 'secs';",
    "matlabbatch{11}.spm.stats.fmri_spec.timing.RT = 2;",
    "matlabbatch{11}.spm.stats.fmri_spec.timing.fmri_t = 16;",
    "matlabbatch{11}.spm.stats.fmri_spec.timing.fmri_t0 = 8;",
    "matlabbatch{11}.spm.stats.fmri_spec.sess.scans(1) = cfg_dep('Smooth: Smoothed Images', substruct('.','val', '{}',{10}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));",
    "matlabbatch{11}.spm.stats.fmri_spec.sess.cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});",
    "matlabbatch{11}.spm.stats.fmri_spec.sess.multi = {'/home/remiadon/nidmresults-examples/spm_default/ds011/SPM/PREPROCESSING/ONSETS/sub-01-MultiCond.mat'};",
    "matlabbatch{11}.spm.stats.fmri_spec.sess.regress = struct('name', {}, 'val', {});",
    "matlabbatch{11}.spm.stats.fmri_spec.sess.multi_reg = {''};",
    "matlabbatch{11}.spm.stats.fmri_spec.sess.hpf = 128;",
    "matlabbatch{11}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});",
    "matlabbatch{11}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];",
    "matlabbatch{11}.spm.stats.fmri_spec.volt = 1;",
    "matlabbatch{11}.spm.stats.fmri_spec.global = 'None';",
    "matlabbatch{11}.spm.stats.fmri_spec.mthresh = 0.8;",
    "matlabbatch{11}.spm.stats.fmri_spec.mask = {''};",
    "matlabbatch{11}.spm.stats.fmri_spec.cvi = 'AR(1)';",
    "matlabbatch{12}.spm.stats.fmri_est.spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{11}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));",
    "matlabbatch{12}.spm.stats.fmri_est.write_residuals = 0;",
    "matlabbatch{12}.spm.stats.fmri_est.method.Classical = 1;",
    "matlabbatch{13}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{12}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));",
    "matlabbatch{13}.spm.stats.con.consess{1}.tcon.name = 'tone counting vs baseline';",
    "matlabbatch{13}.spm.stats.con.consess{1}.tcon.weights = [1 0];",
    "matlabbatch{13}.spm.stats.con.consess{1}.tcon.sessrep = 'none';",
    "matlabbatch{13}.spm.stats.con.delete = 0;",
    "matlabbatch{14}.spm.stats.results.spmmat(1) = cfg_dep('Contrast Manager: SPM.mat File', substruct('.','val', '{}',{13}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));",
    "matlabbatch{14}.spm.stats.results.conspec.titlestr = '';",
    "matlabbatch{14}.spm.stats.results.conspec.contrasts = Inf;",
    "matlabbatch{14}.spm.stats.results.conspec.threshdesc = 'none';",
    "matlabbatch{14}.spm.stats.results.conspec.thresh = 0.001;",
    "matlabbatch{14}.spm.stats.results.conspec.extent = 0;",
    "matlabbatch{14}.spm.stats.results.conspec.conjunction = 1;",
    "matlabbatch{14}.spm.stats.results.conspec.mask.none = 1;",
    "matlabbatch{14}.spm.stats.results.units = 1;",
    "matlabbatch{14}.spm.stats.results.print = 'pdf';",
    "matlabbatch{14}.spm.stats.results.write.tspm.basename = 'thresh';",
]

TASKS = {
    "cfg_basicio.file_dir.file_ops.file_move._1": [
        "files = {'$HOME/nidmresults-examples/spm_default/ds011/sub-01/func/sub-01_task-tonecounting_bold.nii.gz'};",
        "action.copyto = {'$HOME/nidmresults-examples/spm_default/ds011/PREPROCESSING/FUNCTIONAL'};",
    ],
    "cfg_basicio.file_dir.file_ops.file_move._2": [
        "files = {'/home/remiadon/nidmresults-examples/spm_default/ds011/sub-01/anat/sub-01_T1w.nii.gz'};",
        "action.copyto = {'/home/remiadon/nidmresults-examples/spm_default/ds011/PREPROCESSING/ANATOMICAL'};",
    ],
    "cfg_basicio.file_dir.file_ops.cfg_gunzip_files.files(1)._3": [
        " = cfg_dep('Move/Delete Files: Moved/Copied Files', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));"
    ],
    "cfg_basicio.file_dir.file_ops.cfg_gunzip_files.files(1)._4": [
        " = cfg_dep('Move/Delete Files: Moved/Copied Files', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));"
    ],
    "spm.spatial.realign.estwrite._5": [
        "data{1}(1) = cfg_dep('GunZip Files: GunZipped Files', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{':'}));",
        "eoptions.quality = 0.9;",
        "eoptions.sep = 4;",
        "eoptions.fwhm = 5;",
        "eoptions.rtm = 1;",
        "eoptions.interp = 2;",
        "eoptions.wrap = [0 0 0];",
        "eoptions.weight = '';",
        "roptions.which = [0 1];",
        "roptions.interp = 4;",
        "roptions.wrap = [0 0 0];",
        "roptions.mask = 1;",
        "roptions.prefix = 'r';",
    ],
    "spm.spatial.coreg.estimate._6": [
        "ref(1) = cfg_dep('Realign: Estimate & Reslice: Mean Image', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','rmean'));",
        "source(1) = cfg_dep('GunZip Files: GunZipped Files', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{':'}));",
        "other = {''};",
        "eoptions.cost_fun = 'nmi';",
        "eoptions.sep = [4 2];",
        "eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];",
        "eoptions.fwhm = [7 7];",
    ],
    "spm.spatial.preproc._7": [
        "channel.vols(1) = cfg_dep('GunZip Files: GunZipped Files', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{':'}));",
        "channel.biasreg = 0.001;",
        "channel.biasfwhm = 60;",
        "channel.write = [0 1];",
        "tissue(1).tpm = {'/home/radon/spm12/tpm/TPM.nii,1'};",
        "tissue(1).ngaus = 1;",
        "tissue(1).native = [1 0];",
        "tissue(1).warped = [0 0];",
        "tissue(2).tpm = {'/home/radon/spm12/tpm/TPM.nii,2'};",
        "tissue(2).ngaus = 1;",
        "tissue(2).native = [1 0];",
        "tissue(2).warped = [0 0];",
        "tissue(3).tpm = {'/home/radon/spm12/tpm/TPM.nii,3'};",
        "tissue(3).ngaus = 2;",
        "tissue(3).native = [1 0];",
        "tissue(3).warped = [0 0];",
        "tissue(4).tpm = {'/home/radon/spm12/tpm/TPM.nii,4'};",
        "tissue(4).ngaus = 3;",
        "tissue(4).native = [1 0];",
        "tissue(4).warped = [0 0];",
        "tissue(5).tpm = {'/home/radon/spm12/tpm/TPM.nii,5'};",
        "tissue(5).ngaus = 4;",
        "tissue(5).native = [1 0];",
        "tissue(5).warped = [0 0];",
        "tissue(6).tpm = {'/home/radon/spm12/tpm/TPM.nii,6'};",
        "tissue(6).ngaus = 2;",
        "tissue(6).native = [0 0];",
        "tissue(6).warped = [0 0];",
        "warp.mrf = 1;",
        "warp.cleanup = 1;",
        "warp.reg = [0 0.001 0.5 0.05 0.2];",
        "warp.affreg = 'mni';",
        "warp.fwhm = 0;",
        "warp.samp = 3;",
        "warp.write = [0 1];",
    ],
    "spm.spatial.normalise.write._8": [
        "subj.def(1) = cfg_dep('Segment: Forward Deformations', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','fordef', '()',{':'}));",
        "subj.resample(1) = cfg_dep('Realign: Estimate & Reslice: Realigned Images (Sess 1)', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','sess', '()',{1}, '.','cfiles'));",
        "woptions.bb = [-78 -112 -70 78 76 85];",
        "woptions.vox = [2 2 2];",
        "woptions.interp = 4;",
        "woptions.prefix = 'w';",
    ],
    "spm.spatial.normalise.write._9": [
        "subj.def(1) = cfg_dep('Segment: Forward Deformations', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','fordef', '()',{':'}));",
        "subj.resample(1) = cfg_dep('Segment: Bias Corrected (1)', substruct('.','val', '{}',{7}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','channel', '()',{1}, '.','biascorr', '()',{':'}));",
        "woptions.bb = [-78 -112 -70 78 76 85];",
        "woptions.vox = [2 2 2];",
        "woptions.interp = 4;",
        "woptions.prefix = 'w';",
    ],
    "spm.spatial.smooth._10": [
        "data(1) = cfg_dep('Normalise: Write: Normalised Images (Subj 1)', substruct('.','val', '{}',{8}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('()',{1}, '.','files'));",
        "fwhm = [6 6 6];",
        "dtype = 0;",
        "im = 0;",
        "prefix = 's';",
    ],
    "spm.stats.fmri_spec._11": [
        "dir = {'/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/TEST/nidmresults-examples/spm_voxelwise_p0001'};",
        "timing.units = 'secs';",
        "timing.RT = 2;",
        "timing.fmri_t = 16;",
        "timing.fmri_t0 = 8;",
        "sess.scans(1) = cfg_dep('Smooth: Smoothed Images', substruct('.','val', '{}',{10}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','files'));",
        "sess.cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {}, 'orth', {});",
        "sess.multi = {'/home/remiadon/nidmresults-examples/spm_default/ds011/SPM/PREPROCESSING/ONSETS/sub-01-MultiCond.mat'};",
        "sess.regress = struct('name', {}, 'val', {});",
        "sess.multi_reg = {''};",
        "sess.hpf = 128;",
        "fact = struct('name', {}, 'levels', {});",
        "bases.hrf.derivs = [0 0];",
        "volt = 1;",
        "global = 'None';",
        "mthresh = 0.8;",
        "mask = {''};",
        "cvi = 'AR(1)';",
    ],
    "spm.stats.fmri_est._12": [
        "spmmat(1) = cfg_dep('fMRI model specification: SPM.mat File', substruct('.','val', '{}',{11}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));",
        "write_residuals = 0;",
        "method.Classical = 1;",
    ],
    "spm.stats.con._13": [
        "spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{12}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));",
        "consess{1}.tcon.name = 'tone counting vs baseline';",
        "consess{1}.tcon.weights = [1 0];",
        "consess{1}.tcon.sessrep = 'none';",
        "delete = 0;",
    ],
    "spm.stats.results._14": [
        "spmmat(1) = cfg_dep('Contrast Manager: SPM.mat File', substruct('.','val', '{}',{13}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));",
        "conspec.titlestr = '';",
        "conspec.contrasts = Inf;",
        "conspec.threshdesc = 'none';",
        "conspec.thresh = 0.001;",
        "conspec.extent = 0;",
        "conspec.conjunction = 1;",
        "conspec.mask.none = 1;",
        "units = 1;",
        "print = 'pdf';",
        "write.tspm.basename = 'thresh';",
    ],
}

