%-----------------------------------------------------------------------
% Job saved on 12-Apr-2016 11:42:32 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (12.1)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.spm.stats.mfx.ffx.dir = {'/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/TEST/nidmresults-examples/spm_WLS_t_test'};
%%
matlabbatch{1}.spm.stats.mfx.ffx.spmmat = {
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-01/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-02/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-03/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-04/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-06/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-07/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-08/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-09/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-10/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-11/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-12/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-13/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-14/SPM.mat'
                                           '/storage/essicd/data/NIDM-Ex/BIDS_Data/RESULTS/EXAMPLES/ds011/SPM/LEVEL1/sub-05/SPM.mat'
                                           };
%%
matlabbatch{2}.spm.stats.fmri_est.spmmat(1) = cfg_dep('FFX Specification: SPM.mat File', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
matlabbatch{3}.spm.stats.mfx.spec.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{3}.spm.stats.mfx.spec.contrast = [];
matlabbatch{4}.spm.stats.fmri_est.spmmat(1) = cfg_dep('MFX Specification: SPM.mat File', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{4}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{4}.spm.stats.fmri_est.method.Classical = 1;
matlabbatch{5}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{4}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{5}.spm.stats.con.consess{1}.tcon.name = 'con-01: Tone Counting vs Baseline';
matlabbatch{5}.spm.stats.con.consess{1}.tcon.weights = 1;
matlabbatch{5}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
matlabbatch{5}.spm.stats.con.delete = 0;
matlabbatch{6}.spm.stats.results.spmmat(1) = cfg_dep('Contrast Manager: SPM.mat File', substruct('.','val', '{}',{5}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{6}.spm.stats.results.conspec.titlestr = '';
matlabbatch{6}.spm.stats.results.conspec.contrasts = Inf;
matlabbatch{6}.spm.stats.results.conspec.threshdesc = 'none';
matlabbatch{6}.spm.stats.results.conspec.thresh = 0.001;
matlabbatch{6}.spm.stats.results.conspec.extent = 2;
matlabbatch{6}.spm.stats.results.conspec.conjunction = 1;
matlabbatch{6}.spm.stats.results.conspec.mask.none = 1;
matlabbatch{6}.spm.stats.results.units = 1;
matlabbatch{6}.spm.stats.results.print = 'pdf';
matlabbatch{6}.spm.stats.results.write.tspm.basename = 'thresh';
