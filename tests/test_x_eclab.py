import pytest
import os
import xarray as xr
import pickle
from yadg.extractors.eclab.mpr import extract as extract_mpr
from yadg.extractors.eclab.mpt import extract as extract_mpt
from .utils import compare_datatrees


def check_file(fname, kwargs, func):
    ret = func(fn=fname, **kwargs)
    outfile = f"{fname}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
    return ret


@pytest.mark.parametrize(
    "froot, locale",
    [
        ("ca", "en_US"),
        ("ca.issue_134", "en_US"),
        ("ca.issue_149", "de_DE"),
        ("coc.issue_185", "en_US"),
        ("cov.issue_185", "en_US"),
        ("cp", "en_US"),
        ("cp.issue_61", "en_US"),
        ("cp.issue_149", "de_DE"),
        ("cv", "en_US"),
        ("cv.issue_149", "de_DE"),
        ("cva.issue_135", "en_US"),
        ("gcpl", "en_US"),
        ("gcpl.issue_149", "de_DE"),
        ("geis", "en_US"),
        ("lsv", "en_US"),
        ("mb", "en_US"),
        ("mb.issue_95", "en_US"),
        ("mb.issue_149", "de_DE"),
        ("mp.issue_183", "en_US"),
        ("ocv", "en_US"),
        ("ocv.issue_149", "de_DE"),
        ("peis", "en_US"),
        ("wait", "en_US"),
        ("vsp_ocv_wo", "en_US"),
        ("vsp_ocv_with", "en_US"),
        ("vsp_peis_with", "en_US"),
        ("zir", "en_US"),
    ],
)
def test_eclab_consistency(froot, locale, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", locale=locale, encoding="windows-1252")
    aret = check_file(f"{froot}.mpr", kwargs, extract_mpr)
    bret = check_file(f"{froot}.mpt", kwargs, extract_mpt)

    for key in aret.variables:
        if key.endswith("std_err"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e


@pytest.mark.parametrize(
    "froot, locale",
    [
        ("geis.issue_149", "de_DE"),
        ("peis.issue_149", "de_DE"),
    ],
)
def test_eclab_consistency_partial_1(froot, locale, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", locale=locale, encoding="windows-1252")
    aret = check_file(f"{froot}.mpr", kwargs, extract_mpr)
    bret = check_file(f"{froot}.mpt", kwargs, extract_mpt)

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


@pytest.mark.parametrize(
    "froot, locale",
    [
        ("gcpl.pr_182.1", "en_US"),
        ("gcpl.pr_182.2", "en_US"),
    ],
)
def test_eclab_consistency_partial_2(froot, locale, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", locale=locale, encoding="windows-1252")
    aret = check_file(f"{froot}.mpr", kwargs, extract_mpr)
    bret = check_file(f"{froot}.mpt", kwargs, extract_mpt)

    for key in aret.variables:
        if key.endswith("std_err"):
            continue
        elif key in {"control_I"}:
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("mb.issue_95.mpt", "mb.issue_95.de.mpt"),
    ],
)
def test_eclab_mpt_locale(afile, bfile, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", encoding="windows-1252")
    aret = extract_mpt(fn=afile, locale="en_US", **kwargs)
    bret = extract_mpt(fn=bfile, locale="de_DE", **kwargs)
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
    aret = extract_mpt(fn=afile, locale="en_US", **kwargs)
    bret = extract_mpt(fn=bfile, locale="en_US", **kwargs)

    for key in aret.variables:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            if key in {"Efficiency", "Efficiency_std_err"}:
                pass
            else:
                e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
                raise e
