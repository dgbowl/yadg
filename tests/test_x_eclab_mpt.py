import pytest
import os
import pickle
import xarray as xr
from yadg.extractors.eclab.mpt import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile, locale",
    [
        ("ca.mpt", "en_GB"),
        ("ca.issue_134.mpt", "en_GB"),
        ("ca.issue_149.mpt", "de_DE"),
        ("cp.mpt", "en_GB"),
        ("cp.issue_61.mpt", "en_GB"),
        ("cp.issue_149.mpt", "de_DE"),
        ("cv.mpt", "en_GB"),
        ("cv.issue_149.mpt", "de_DE"),
        ("cva.issue_135.mpt", "en_GB"),
        ("gcpl.mpt", "en_GB"),
        ("gcpl.issue_149.mpt", "de_DE"),
        ("geis.mpt", "en_GB"),
        ("geis.issue_149.mpt", "de_DE"),
        ("lsv.mpt", "en_GB"),
        ("mb.mpt", "en_GB"),
        ("mb.issue_95.mpt", "en_GB"),
        ("mb.issue_149.mpt", "de_DE"),
        ("ocv.mpt", "en_GB"),
        ("ocv.issue_149.mpt", "de_DE"),
        ("peis.mpt", "en_GB"),
        ("peis.issue_149.mpt", "de_DE"),
        ("wait.mpt", "en_GB"),
        ("zir.mpt", "en_GB"),
        ("vsp_ocv_with.mpt", "en_GB"),
        ("vsp_ocv_wo.mpt", "en_GB"),
        ("vsp_peis_with.mpt", "en_GB"),
    ],
)
def test_eclab_mpt(infile, locale, datadir):
    os.chdir(datadir)
    ret = extract(
        fn=infile,
        timezone="Europe/Berlin",
        encoding="windows-1252",
        locale=locale,
    )
    print(f"{ret=}")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("mb.issue_95.mpt", "mb.issue_95.de.mpt"),
    ],
)
def test_eclab_mpt_locale(afile, bfile, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", encoding="windows-1252")
    aret = extract(fn=afile, locale="en_US", **kwargs)
    bret = extract(fn=bfile, locale="de_DE", **kwargs)
    compare_datatrees(aret, bret)


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("mb.old.mpt", "mb.mpt"),
        ("gcpl.old.mpt", "gcpl.mpt"),
        ("ocv.old.mpt", "ocv.mpt"),
        ("wait.old.mpt", "wait.mpt"),
    ],
)
def test_eclab_mpt_old(afile, bfile, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", encoding="windows-1252")
    aret = extract(fn=afile, locale="en_US", **kwargs)
    bret = extract(fn=bfile, locale="en_US", **kwargs)

    for key in aret.variables:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            if key in {"Efficiency", "Efficiency_std_err"}:
                pass
            else:
                e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
                raise e
