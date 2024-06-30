import pytest
import os
import xarray as xr
import shutil
from yadg.extractors.eclab.mpr import extract as extract_mpr
from yadg.extractors.eclab.mpt import extract as extract_mpt


@pytest.fixture
def _datadir(tmpdir, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    base_dir, _ = os.path.split(test_dir)
    for ddir in ["test_x_eclab_mpr", "test_x_eclab_mpt"]:
        shutil.copytree(os.path.join(base_dir, ddir), str(tmpdir), dirs_exist_ok=True)
    return tmpdir


@pytest.mark.parametrize(
    "afile, bfile, locale",
    [
        ("ca.mpr", "ca.mpt", "en_US"),
        ("ca.issue_134.mpr", "ca.issue_134.mpt", "en_US"),
        ("ca.issue_149.mpr", "ca.issue_149.mpt", "de_DE"),
        ("cp.mpr", "cp.mpt", "en_US"),
        ("cp.issue_61.mpr", "cp.issue_61.mpt", "en_US"),
        ("cp.issue_149.mpr", "cp.issue_149.mpt", "de_DE"),
        ("cv.mpr", "cv.mpt", "en_US"),
        ("cv.issue_149.mpr", "cv.issue_149.mpt", "de_DE"),
        ("cva.issue_135.mpr", "cva.issue_135.mpt", "en_US"),
        ("gcpl.mpr", "gcpl.mpt", "en_US"),
        ("gcpl.issue_149.mpr", "gcpl.issue_149.mpt", "de_DE"),
        ("geis.mpr", "geis.mpt", "en_US"),
        ("lsv.mpr", "lsv.mpt", "en_US"),
        ("mb.mpr", "mb.mpt", "en_US"),
        ("mb.issue_95.mpr", "mb.issue_95.mpt", "en_US"),
        ("mb.issue_149.mpr", "mb.issue_149.mpt", "de_DE"),
        ("ocv.mpr", "ocv.mpt", "en_US"),
        ("ocv.issue_149.mpr", "ocv.issue_149.mpt", "de_DE"),
        ("peis.mpr", "peis.mpt", "en_US"),
        ("wait.mpr", "wait.mpt", "en_US"),
        ("zir.mpr", "zir.mpt", "en_US"),
        ("vsp_ocv_wo.mpr", "vsp_ocv_wo.mpt", "en_US"),
        ("vsp_ocv_with.mpr", "vsp_ocv_with.mpt", "en_US"),
        ("vsp_peis_with.mpr", "vsp_peis_with.mpt", "en_US"),
    ],
)
def test_eclab_consistency(afile, bfile, locale, _datadir):
    os.chdir(_datadir)
    aret = extract_mpr(fn=afile, timezone="Europe/Berlin")
    bret = extract_mpt(
        fn=bfile, timezone="Europe/Berlin", encoding="windows-1252", locale=locale
    )
    print(f"{aret.data_vars=}")
    print(f"{bret.data_vars=}")
    for key in aret.variables:
        if key.endswith("std_err"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e


@pytest.mark.parametrize(
    "afile, bfile, locale",
    [
        ("geis.issue_149.mpr", "geis.issue_149.mpt", "de_DE"),
        ("peis.issue_149.mpr", "peis.issue_149.mpt", "de_DE"),
    ],
)
def test_eclab_consistency_partial(afile, bfile, locale, _datadir):
    os.chdir(_datadir)
    aret = extract_mpr(fn=afile, timezone="Europe/Berlin")
    bret = extract_mpt(
        fn=bfile, timezone="Europe/Berlin", encoding="windows-1252", locale=locale
    )
    print(f"{aret.data_vars=}")
    print(f"{bret.data_vars=}")
    for key in {
        "freq",
        "Re(Z)",
        "-Im(Z)",
        "|Z|",
        "Phase(Z)",
        "time",
        "<Ewe>",
        "<I>",
        "Cs",
        "Cp",
        "cycle number",
        "|Ewe|",
        "|I|",
        "Ns",
        "I Range",
    }:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
