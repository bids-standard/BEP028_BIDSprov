# Progress Report / Log

Started at Thu Apr 16 11:05:35 UTC 2020

#### Feat main script


/bin/cp /tmp/feat_oJmMLg.fsf design.fsf

/usr/share/fsl/5.0/bin/feat_model design

mkdir .files;cp /usr/share/fsl/5.0/doc/fsl.css .files;cp -r /usr/share/fsl/5.0/doc/images .files/images

/usr/share/fsl/5.0/bin/fsl_sub -T 10 -l logs -N feat0_init   /usr/share/fsl/5.0/bin/feat /data/fmri1/fluency_task/fmri.feat/design.fsf -D /data/fmri1/fluency_task/fmri.feat -I 1 -init
590

/usr/share/fsl/5.0/bin/fsl_sub -T 40 -l logs -N feat2_pre -j 590  /usr/share/fsl/5.0/bin/feat /data/fmri1/fluency_task/fmri.feat/design.fsf -D /data/fmri1/fluency_task/fmri.feat -I 1 -prestats
710

/usr/share/fsl/5.0/bin/fsl_sub -T 1 -l logs -N feat3_film -j 710  /usr/share/fsl/5.0/bin/feat /data/fmri1/fluency_task/fmri.feat/design.fsf -D /data/fmri1/fluency_task/fmri.feat -I 1 -stats
2114

/usr/share/fsl/5.0/bin/fsl_sub -T 119 -l logs -N feat4_post -j 2114  /usr/share/fsl/5.0/bin/feat /data/fmri1/fluency_task/fmri.feat/design.fsf -D /data/fmri1/fluency_task/fmri.feat -poststats 0 
2418

/usr/share/fsl/5.0/bin/fsl_sub -T 1 -l logs -N feat5_stop -j 710,2114,2418  /usr/share/fsl/5.0/bin/feat /data/fmri1/fluency_task/fmri.feat/design.fsf -D /data/fmri1/fluency_task/fmri.feat -stop

---------------
## Initialisation

/usr/share/fsl/5.0/bin/fslmaths /data/fmri1/fluency_task/fmri prefiltered_func_data -odt float
Total original volumes = 106

/usr/share/fsl/5.0/bin/fslroi prefiltered_func_data example_func 53 1

---------------
## Preprocessing:Stage 1

/usr/share/fsl/5.0/bin/mainfeatreg -F 6.00 -d /data/fmri1/fluency_task/fmri.feat -l /data/fmri1/fluency_task/fmri.feat/logs/feat2_pre -R /data/fmri1/fluency_task/fmri.feat/report_unwarp.html -r /data/fmri1/fluency_task/fmri.feat/report_reg.html  -i /data/fmri1/fluency_task/fmri.feat/example_func.nii.gz  -h /data/fmri1/fluency_task/structural_brain -w  7 -x 90 -s /usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain -y 12 -z 90 
Option -F ( FEAT version parameter ) selected with  argument "6.00"
Option -d ( output directory ) selected with  argument "/data/fmri1/fluency_task/fmri.feat"
Option -l ( logfile )input with argument "/data/fmri1/fluency_task/fmri.feat/logs/feat2_pre"
Option -R ( html unwarping report ) selected with  argument "/data/fmri1/fluency_task/fmri.feat/report_unwarp.html"
Option -r ( html registration report ) selected with  argument "/data/fmri1/fluency_task/fmri.feat/report_reg.html"
Option -i ( main input ) input with argument "/data/fmri1/fluency_task/fmri.feat/example_func.nii.gz"
Option -h ( high-res structural image ) selected with  argument "/data/fmri1/fluency_task/structural_brain"
Option -w ( highres dof ) selected with  argument "7"
Option -x ( highres search ) selected with  argument "90"
Option -s ( standard image ) selected with  argument "/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain"
Option -y ( standard dof ) selected with  argument "12"
Option -z ( standard search ) selected with  argument "90"

## Registration

/bin/mkdir -p /data/fmri1/fluency_task/fmri.feat/reg


/usr/share/fsl/5.0/bin/fslmaths /data/fmri1/fluency_task/structural_brain highres


/usr/share/fsl/5.0/bin/fslmaths /usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain standard

did not find file: example_func2highres.mat. Generating transform.

/usr/share/fsl/5.0/bin/flirt -in example_func -ref highres -out example_func2highres -omat example_func2highres.mat -cost corratio -dof 7 -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -interp trilinear 


/usr/share/fsl/5.0/bin/convert_xfm -inverse -omat highres2example_func.mat example_func2highres.mat


/usr/share/fsl/5.0/bin/slicer example_func2highres highres -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png -x 0.65 sld.png -y 0.35 sle.png -y 0.45 slf.png -y 0.55 slg.png -y 0.65 slh.png -z 0.35 sli.png -z 0.45 slj.png -z 0.55 slk.png -z 0.65 sll.png ; /usr/share/fsl/5.0/bin/pngappend sla.png + slb.png + slc.png + sld.png + sle.png + slf.png + slg.png + slh.png + sli.png + slj.png + slk.png + sll.png example_func2highres1.png ; /usr/share/fsl/5.0/bin/slicer highres example_func2highres -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png -x 0.65 sld.png -y 0.35 sle.png -y 0.45 slf.png -y 0.55 slg.png -y 0.65 slh.png -z 0.35 sli.png -z 0.45 slj.png -z 0.55 slk.png -z 0.65 sll.png ; /usr/share/fsl/5.0/bin/pngappend sla.png + slb.png + slc.png + sld.png + sle.png + slf.png + slg.png + slh.png + sli.png + slj.png + slk.png + sll.png example_func2highres2.png ; /usr/share/fsl/5.0/bin/pngappend example_func2highres1.png - example_func2highres2.png example_func2highres.png; /bin/rm -f sl?.png example_func2highres2.png


/bin/rm example_func2highres1.png

did not find file: highres2standard.mat.

Generating transform.

/usr/share/fsl/5.0/bin/flirt -in highres -ref standard -out highres2standard -omat highres2standard.mat -cost corratio -dof 12 -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -interp trilinear 


/usr/share/fsl/5.0/bin/convert_xfm -inverse -omat standard2highres.mat highres2standard.mat


/usr/share/fsl/5.0/bin/slicer highres2standard standard -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png -x 0.65 sld.png -y 0.35 sle.png -y 0.45 slf.png -y 0.55 slg.png -y 0.65 slh.png -z 0.35 sli.png -z 0.45 slj.png -z 0.55 slk.png -z 0.65 sll.png ; /usr/share/fsl/5.0/bin/pngappend sla.png + slb.png + slc.png + sld.png + sle.png + slf.png + slg.png + slh.png + sli.png + slj.png + slk.png + sll.png highres2standard1.png ; /usr/share/fsl/5.0/bin/slicer standard highres2standard -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png -x 0.65 sld.png -y 0.35 sle.png -y 0.45 slf.png -y 0.55 slg.png -y 0.65 slh.png -z 0.35 sli.png -z 0.45 slj.png -z 0.55 slk.png -z 0.65 sll.png ; /usr/share/fsl/5.0/bin/pngappend sla.png + slb.png + slc.png + sld.png + sle.png + slf.png + slg.png + slh.png + sli.png + slj.png + slk.png + sll.png highres2standard2.png ; /usr/share/fsl/5.0/bin/pngappend highres2standard1.png - highres2standard2.png highres2standard.png; /bin/rm -f sl?.png highres2standard2.png


/bin/rm highres2standard1.png


/usr/share/fsl/5.0/bin/convert_xfm -omat example_func2standard.mat -concat highres2standard.mat example_func2highres.mat


/usr/share/fsl/5.0/bin/flirt -ref standard -in example_func -out example_func2standard -applyxfm -init example_func2standard.mat -interp trilinear

Found file: example_func2standard.mat.

/usr/share/fsl/5.0/bin/convert_xfm -inverse -omat standard2example_func.mat example_func2standard.mat


/usr/share/fsl/5.0/bin/slicer example_func2standard standard -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png -x 0.65 sld.png -y 0.35 sle.png -y 0.45 slf.png -y 0.55 slg.png -y 0.65 slh.png -z 0.35 sli.png -z 0.45 slj.png -z 0.55 slk.png -z 0.65 sll.png ; /usr/share/fsl/5.0/bin/pngappend sla.png + slb.png + slc.png + sld.png + sle.png + slf.png + slg.png + slh.png + sli.png + slj.png + slk.png + sll.png example_func2standard1.png ; /usr/share/fsl/5.0/bin/slicer standard example_func2standard -s 2 -x 0.35 sla.png -x 0.45 slb.png -x 0.55 slc.png -x 0.65 sld.png -y 0.35 sle.png -y 0.45 slf.png -y 0.55 slg.png -y 0.65 slh.png -z 0.35 sli.png -z 0.45 slj.png -z 0.55 slk.png -z 0.65 sll.png ; /usr/share/fsl/5.0/bin/pngappend sla.png + slb.png + slc.png + sld.png + sle.png + slf.png + slg.png + slh.png + sli.png + slj.png + slk.png + sll.png example_func2standard2.png ; /usr/share/fsl/5.0/bin/pngappend example_func2standard1.png - example_func2standard2.png example_func2standard.png; /bin/rm -f sl?.png example_func2standard2.png

## Preprocessing:Stage 2

/usr/share/fsl/5.0/bin/mcflirt -in prefiltered_func_data -out prefiltered_func_data_mcf -mats -plots -reffile example_func -rmsrel -rmsabs -spline_final

/bin/mkdir -p mc ; /bin/mv -f prefiltered_func_data_mcf.mat prefiltered_func_data_mcf.par prefiltered_func_data_mcf_abs.rms prefiltered_func_data_mcf_abs_mean.rms prefiltered_func_data_mcf_rel.rms prefiltered_func_data_mcf_rel_mean.rms mc

/usr/share/fsl/5.0/bin/fsl_tsplot -i prefiltered_func_data_mcf.par -t 'MCFLIRT estimated rotations (radians)' -u 1 --start=1 --finish=3 -a x,y,z -w 640 -h 144 -o rot.png 

/usr/share/fsl/5.0/bin/fsl_tsplot -i prefiltered_func_data_mcf.par -t 'MCFLIRT estimated translations (mm)' -u 1 --start=4 --finish=6 -a x,y,z -w 640 -h 144 -o trans.png 

/usr/share/fsl/5.0/bin/fsl_tsplot -i prefiltered_func_data_mcf_abs.rms,prefiltered_func_data_mcf_rel.rms -t 'MCFLIRT estimated mean displacement (mm)' -u 1 -w 640 -h 144 -a absolute,relative -o disp.png 

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_mcf -Tmean mean_func

/usr/share/fsl/5.0/bin/bet2 mean_func mask -f 0.3 -n -m; /usr/share/fsl/5.0/bin/immv mask_mask mask

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_mcf -mas mask prefiltered_func_data_bet

/usr/share/fsl/5.0/bin/fslstats prefiltered_func_data_bet -p 2 -p 98
0.000000 9827.754883 

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_bet -thr 982.7754883 -Tmin -bin mask -odt char

/usr/share/fsl/5.0/bin/fslstats prefiltered_func_data_mcf -k mask -p 50
7535.813477 

/usr/share/fsl/5.0/bin/fslmaths mask -dilF mask

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_mcf -mas mask prefiltered_func_data_thresh

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_thresh -Tmean mean_func

/usr/share/fsl/5.0/bin/susan prefiltered_func_data_thresh 5651.86010775 2.9723991507431 3 1 1 mean_func 5651.86010775 prefiltered_func_data_smooth

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_smooth -mas mask prefiltered_func_data_smooth

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_smooth -mul 1.3269967509839415 prefiltered_func_data_intnorm

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_intnorm -Tmean tempMean

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_intnorm -bptf 10.714285714285714 -1 -add tempMean prefiltered_func_data_tempfilt

/usr/share/fsl/5.0/bin/imrm tempMean

/usr/share/fsl/5.0/bin/fslmaths prefiltered_func_data_tempfilt filtered_func_data

/usr/share/fsl/5.0/bin/fslmaths filtered_func_data -Tmean mean_func

/bin/rm -rf prefiltered_func_data*

## Stats

mkdir -p custom_timing_files ; /usr/share/fsl/5.0/bin/fslFixText /data/fmri1/fluency_task/word_generation.txt custom_timing_files/ev1.txt

mkdir -p custom_timing_files ; /usr/share/fsl/5.0/bin/fslFixText /data/fmri1/fluency_task/word_shadowing.txt custom_timing_files/ev2.txt

/usr/share/fsl/5.0/bin/film_gls --in=filtered_func_data --rn=stats --pd=design.mat --thr=1000.0 --sa --ms=5 --con=design.con --fcon=design.fts  
Log directory is: stats
paradigm.getDesignMatrix().Nrows()=106
paradigm.getDesignMatrix().Ncols()=4
sizeTS=106
numTS=45081
Calculating residuals...
Completed
Estimating residual autocorrelation...
Calculating raw AutoCorrs... Completed
mode = 9605.38
sig = 1451
Spatially smoothing auto corr estimates
.........
Completed
Tukey M = 10
Tukey estimates... Completed
Completed
Prewhitening and Computing PEs...
Percentage done:
1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,Completed
Saving results... 
Completed

/usr/share/fsl/5.0/bin/smoothest -d 102   -m mask -r stats/res4d > stats/smoothness

## Post-stats

/usr/share/fsl/5.0/bin/fslmaths stats/zstat1 -mas mask thresh_zstat1

echo 45081 > thresh_zstat1.vol
zstat1: DLH=0.387734 VOLUME=45081 RESELS=11.9468

/usr/share/fsl/5.0/bin/fslmaths stats/zstat2 -mas mask thresh_zstat2

echo 45081 > thresh_zstat2.vol
zstat2: DLH=0.387734 VOLUME=45081 RESELS=11.9468

/usr/share/fsl/5.0/bin/fslmaths stats/zstat3 -mas mask thresh_zstat3

echo 45081 > thresh_zstat3.vol
zstat3: DLH=0.387734 VOLUME=45081 RESELS=11.9468

/usr/share/fsl/5.0/bin/fslmaths stats/zstat4 -mas mask thresh_zstat4

echo 45081 > thresh_zstat4.vol
zstat4: DLH=0.387734 VOLUME=45081 RESELS=11.9468

/usr/share/fsl/5.0/bin/fslmaths stats/zstat5 -mas mask thresh_zstat5

echo 45081 > thresh_zstat5.vol
zstat5: DLH=0.387734 VOLUME=45081 RESELS=11.9468

/usr/share/fsl/5.0/bin/fslmaths stats/zfstat1 -mas mask thresh_zfstat1

echo 45081 > thresh_zfstat1.vol
zfstat1: DLH=0.387734 VOLUME=45081 RESELS=11.9468

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat1 -c stats/cope1 -t 2.3 -p 0.05 -d 0.387734 --volume=45081 --othresh=thresh_zstat1 -o cluster_mask_zstat1 --connectivity=26  --olmax=lmax_zstat1.txt --scalarname=Z > cluster_zstat1.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat1 

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat2 -c stats/cope2 -t 2.3 -p 0.05 -d 0.387734 --volume=45081 --othresh=thresh_zstat2 -o cluster_mask_zstat2 --connectivity=26  --olmax=lmax_zstat2.txt --scalarname=Z > cluster_zstat2.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat2 

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat3 -c stats/cope3 -t 2.3 -p 0.05 -d 0.387734 --volume=45081 --othresh=thresh_zstat3 -o cluster_mask_zstat3 --connectivity=26  --olmax=lmax_zstat3.txt --scalarname=Z > cluster_zstat3.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat3 

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat4 -c stats/cope4 -t 2.3 -p 0.05 -d 0.387734 --volume=45081 --othresh=thresh_zstat4 -o cluster_mask_zstat4 --connectivity=26  --olmax=lmax_zstat4.txt --scalarname=Z > cluster_zstat4.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat4 

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat5 -c stats/cope5 -t 2.3 -p 0.05 -d 0.387734 --volume=45081 --othresh=thresh_zstat5 -o cluster_mask_zstat5 --connectivity=26  --olmax=lmax_zstat5.txt --scalarname=Z > cluster_zstat5.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat5 

/usr/share/fsl/5.0/bin/cluster -i thresh_zfstat1  -t 2.3 -p 0.05 -d 0.387734 --volume=45081 --othresh=thresh_zfstat1 -o cluster_mask_zfstat1 --connectivity=26  --olmax=lmax_zfstat1.txt --scalarname=Z > cluster_zfstat1.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zfstat1 

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat1 -c stats/cope1 -t 2.3  -p 0.05 -d 0.387734 --volume=45081 -x reg/example_func2standard.mat --stdvol=reg/standard --mm --connectivity=26 --olmax=lmax_zstat1_std.txt --scalarname=Z > cluster_zstat1_std.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat1 -std

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat2 -c stats/cope2 -t 2.3  -p 0.05 -d 0.387734 --volume=45081 -x reg/example_func2standard.mat --stdvol=reg/standard --mm --connectivity=26 --olmax=lmax_zstat2_std.txt --scalarname=Z > cluster_zstat2_std.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat2 -std

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat3 -c stats/cope3 -t 2.3  -p 0.05 -d 0.387734 --volume=45081 -x reg/example_func2standard.mat --stdvol=reg/standard --mm --connectivity=26 --olmax=lmax_zstat3_std.txt --scalarname=Z > cluster_zstat3_std.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat3 -std

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat4 -c stats/cope4 -t 2.3  -p 0.05 -d 0.387734 --volume=45081 -x reg/example_func2standard.mat --stdvol=reg/standard --mm --connectivity=26 --olmax=lmax_zstat4_std.txt --scalarname=Z > cluster_zstat4_std.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat4 -std

/usr/share/fsl/5.0/bin/cluster -i thresh_zstat5 -c stats/cope5 -t 2.3  -p 0.05 -d 0.387734 --volume=45081 -x reg/example_func2standard.mat --stdvol=reg/standard --mm --connectivity=26 --olmax=lmax_zstat5_std.txt --scalarname=Z > cluster_zstat5_std.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zstat5 -std

/usr/share/fsl/5.0/bin/cluster -i thresh_zfstat1  -t 2.3  -p 0.05 -d 0.387734 --volume=45081 -x reg/example_func2standard.mat --stdvol=reg/standard --mm --connectivity=26 --olmax=lmax_zfstat1_std.txt --scalarname=Z > cluster_zfstat1_std.txt

/usr/share/fsl/5.0/bin/cluster2html . cluster_zfstat1 -std

/usr/share/fsl/5.0/bin/fslstats thresh_zstat1 -l 0.0001 -R 2>/dev/null
2.300048 6.133199 

/usr/share/fsl/5.0/bin/fslstats thresh_zstat2 -l 0.0001 -R 2>/dev/null
2.300061 6.440603 

/usr/share/fsl/5.0/bin/fslstats thresh_zstat3 -l 0.0001 -R 2>/dev/null
2.300882 6.401662 

/usr/share/fsl/5.0/bin/fslstats thresh_zstat4 -l 0.0001 -R 2>/dev/null
2.303167 3.934648 

/usr/share/fsl/5.0/bin/fslstats thresh_zstat5 -l 0.0001 -R 2>/dev/null
2.301617 6.236727 

/usr/share/fsl/5.0/bin/fslstats thresh_zfstat1 -l 0.0001 -R 2>/dev/null
2.300071 6.092561 
Rendering using zmin=2.300048 zmax=6.440603

/usr/share/fsl/5.0/bin/overlay 1 0 example_func -a thresh_zstat1 2.300048 6.440603 rendered_thresh_zstat1

/usr/share/fsl/5.0/bin/slicer rendered_thresh_zstat1 -A 750 rendered_thresh_zstat1.png

/bin/cp /usr/share/fsl/5.0/etc/luts/ramp.gif .ramp.gif

/usr/share/fsl/5.0/bin/overlay 1 0 example_func -a thresh_zstat2 2.300048 6.440603 rendered_thresh_zstat2

/usr/share/fsl/5.0/bin/slicer rendered_thresh_zstat2 -A 750 rendered_thresh_zstat2.png

/usr/share/fsl/5.0/bin/overlay 1 0 example_func -a thresh_zstat3 2.300048 6.440603 rendered_thresh_zstat3

/usr/share/fsl/5.0/bin/slicer rendered_thresh_zstat3 -A 750 rendered_thresh_zstat3.png

/usr/share/fsl/5.0/bin/overlay 1 0 example_func -a thresh_zstat4 2.300048 6.440603 rendered_thresh_zstat4

/usr/share/fsl/5.0/bin/slicer rendered_thresh_zstat4 -A 750 rendered_thresh_zstat4.png

/usr/share/fsl/5.0/bin/overlay 1 0 example_func -a thresh_zstat5 2.300048 6.440603 rendered_thresh_zstat5

/usr/share/fsl/5.0/bin/slicer rendered_thresh_zstat5 -A 750 rendered_thresh_zstat5.png

/usr/share/fsl/5.0/bin/overlay 1 0 example_func -a thresh_zfstat1 2.300048 6.440603 rendered_thresh_zfstat1

/usr/share/fsl/5.0/bin/slicer rendered_thresh_zfstat1 -A 750 rendered_thresh_zfstat1.png

mkdir -p tsplot ; /usr/share/fsl/5.0/bin/tsplot . -f filtered_func_data -o tsplot