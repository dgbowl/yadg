import pytest
import os
import xarray as xr
from distutils import dir_util
from yadg.extractors.eclab.mpr import extract as extract_mpr
from yadg.extractors.eclab.mpt import extract as extract_mpt


@pytest.fixture
def _datadir(tmpdir, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    base_dir, _ = os.path.split(test_dir)
    for ddir in ["test_eclab_mpr", "test_eclab_mpt"]:
        dir_util.copy_tree(os.path.join(base_dir, ddir), str(tmpdir))
    return tmpdir


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("ca.mpr", "ca.mpt"),
        ("ca.issue_134.mpr", "ca.issue_134.mpt"),
        ("cp.mpr", "cp.mpt"),
        ("cv.mpr", "cv.mpt"),
        ("gcpl.mpr", "gcpl.mpt"),
        ("geis.mpr", "geis.mpt"),
        ("lsv.mpr", "lsv.mpt"),
        ("mb.mpr", "mb.mpt"),
        ("ocv.mpr", "ocv.mpt"),
        ("peis.mpr", "peis.mpt"),
        ("wait.mpr", "wait.mpt"),
        ("zir.mpr", "zir.mpt"),
        ("mb_67.mpr", "mb_67.mpt"),
        ("issue_61_Irange_65.mpr", "issue_61_Irange_65.mpt"),
        ("vsp_ocv_wo.mpr", "vsp_ocv_wo.mpt"),
        ("vsp_ocv_with.mpr", "vsp_ocv_with.mpt"),
        ("vsp_peis_with.mpr", "vsp_peis_with.mpt"),
    ],
)
def test_eclab_consistency(afile, bfile, _datadir):
    os.chdir(_datadir)
    aret = extract_mpr(fn=afile, timezone="Europe/Berlin")
    bret = extract_mpt(
        fn=bfile, timezone="Europe/Berlin", encoding="windows-1252", locale="en_US"
    )
    for key in aret.variables:
        if key.endswith("std_err"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
