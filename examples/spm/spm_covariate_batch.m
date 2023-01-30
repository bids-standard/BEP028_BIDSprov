%-----------------------------------------------------------------------
% Job saved on 08-Dec-2015 14:42:04 by cfg_util (rev $Rev: 6460 $)
% spm SPM - SPM12 (12.1)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.spm.stats.factorial_design.dir = {'/storage/essicd/data/NIDM-Ex/Testing/ds000006/RESULTS/Group/Con1/Covariate'};
%%
matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub01/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub02/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub03/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub04/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub05/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub06/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub07/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub08/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub09/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub10/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub11/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub12/con_0001.nii,1'
                                                          '/storage/essicd/data/NIDM-Ex/Data/ds000052/RESULTS/Sub13/con_0001.nii,1'
                                                          };
%%
%%
matlabbatch{1}.spm.stats.factorial_design.cov.c = [1
                                                   2
                                                   3
                                                   4
                                                   5
                                                   6
                                                   7
                                                   8
                                                   9
                                                   10
                                                   11
                                                   12
                                                   13];
%%
matlabbatch{1}.spm.stats.factorial_design.cov.cname = 'Subject ID Covariate';
matlabbatch{1}.spm.stats.factorial_design.cov.iCFI = 1;
matlabbatch{1}.spm.stats.factorial_design.cov.iCC = 1;
matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
matlabbatch{1}.spm.stats.factorial_design.masking.em = {''};
matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;
matlabbatch{2}.spm.stats.fmri_est.spmmat(1) = cfg_dep('Factorial design specification: SPM.mat File', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
matlabbatch{3}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'mr vs plain covariate';
matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = 1;
matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.delete = 0;
matlabbatch{4}.spm.stats.results.spmmat(1) = cfg_dep('Contrast Manager: SPM.mat File', substruct('.','val', '{}',{3}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{4}.spm.stats.results.conspec.titlestr = '';
matlabbatch{4}.spm.stats.results.conspec.contrasts = 1;
matlabbatch{4}.spm.stats.results.conspec.threshdesc = 'none';
matlabbatch{4}.spm.stats.results.conspec.thresh = 0.001;
matlabbatch{4}.spm.stats.results.conspec.extent = 0;
matlabbatch{4}.spm.stats.results.conspec.conjunction = 1;
matlabbatch{4}.spm.stats.results.conspec.mask.none = 1;
matlabbatch{4}.spm.stats.results.units = 1;
matlabbatch{4}.spm.stats.results.print = 'pdf';
matlabbatch{4}.spm.stats.results.write.none = 1;
