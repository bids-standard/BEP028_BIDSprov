from unittest.mock import mock_open, patch
from bids_prov.afni.afni_parser import readlines, clean_label_suffix
import pytest
import re


def test_clean_label_suffix():
    assert clean_label_suffix(
        "pb00.$subj.r$run.tcat+orig") == "pb00.$subj.r$run.tcat"
    assert clean_label_suffix(
        "pb00.$subj.r$run.tcat+tlrc") == "pb00.$subj.r$run.tcat"
    assert clean_label_suffix(
        'X.nocensor.xmat.1D"[$reg_cols]"') == "X.nocensor.xmat.1D"
    assert clean_label_suffix(
        "X.nocensor.xmat.1D'[3]'") == "X.nocensor.xmat.1D"


def test_readlines():
    afni_part_sample = """cp ./afni_voxelwise_p0001/tone_counting_onset_times.txt\
        ./afni_voxelwise_p0001/tone_counting_probe_duration.txt\
        $output_dir/stimuli

    # copy anatomy to results dir
    3dcopy\
        ./afni_voxelwise_p0001/sub-01_T1w.nii.gz\
        $output_dir/sub-01_T1w

    # ============================ auto block: tcat ============================
    # apply 3dTcat to copy input dsets to results dir, while
    # removing the first 0 TRs
    3dTcat -prefix $output_dir/pb00.$subj.r01.tcat\
        ./afni_voxelwise_p0001/sub-01_task-tonecounting_bold.nii.gz'[0..$]'

    # and make note of repetitions (TRs) per run
    set tr_counts = ( 104 )

    # -------------------------------------------------------
    # enter the results directory (can begin processing data)
    cd $output_dir


    # ========================== auto block: outcount ==========================
    # data check: compute outlier fraction for each volume
    touch out.pre_ss_warn.txt
    foreach run ( $runs )
        3dToutcount -automask -fraction -polort 2 -legendre\
                    pb00.$subj.r$run.tcat+orig > outcount.r$run.1D

        # outliers at TR 0 might suggest pre-steady state TRs
        if ( `1deval -a outcount.r$run.1D"{0}" -expr "step(a-0.4)"` ) then
            echo "** TR #0 outliers: possible pre-steady state TRs in run $run"\
                >> out.pre_ss_warn.txt
        endif
    end
    """
    # Test valid file
    m = mock_open(read_data=afni_part_sample)
    with patch("builtins.open", m, create=True):
        filename = "afni_sample.subb_001"
        commands = readlines(filename)
        expected_commands = ["cp ./afni_voxelwise_p0001/tone_counting_onset_times.txt ./afni_voxelwise_p0001/tone_counting_probe_duration.txt $output_dir/stimuli",
                             "3dcopy ./afni_voxelwise_p0001/sub-01_T1w.nii.gz $output_dir/sub-01_T1w",
                             "3dTcat -prefix $output_dir/pb00.$subj.r01.tcat ./afni_voxelwise_p0001/sub-01_task-tonecounting_bold.nii.gz'[0..$]'",
                             "3dToutcount -automask -fraction -polort 2 -legendre pb00.$subj.r$run.tcat+orig > outcount.r$run.1D"
                             ]
        commands = [cmd.strip() for (block, cmd) in commands]
        # Replace multi (>=2 ) blank space to one
        commands = [re.sub(r"\s{2,}", " ", cmd) for cmd in commands]
        expected_commands = [cmd.strip() for cmd in expected_commands]
        print("COMMANDS\n", "\n".join(commands))
        print("expected_commands\n", "\n".join(expected_commands))
        assert "\n".join(commands) == "\n".join(expected_commands)

    # Test invalid file path
    with pytest.raises(FileNotFoundError):
        filename = "invalid_file.txt"
        lines = readlines(filename)
