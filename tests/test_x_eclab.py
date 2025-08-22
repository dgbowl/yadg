import pytest
import os
import xarray as xr
import numpy as np
import pickle
from yadg.extractors.eclab.mpr import extract as extract_mpr
from yadg.extractors.eclab.mpt import extract as extract_mpt
from .utils import compare_datatrees
from pathlib import Path


def check_file(fname, kwargs, func):
    ret = func(source=Path(fname), **kwargs)
    outfile = f"{fname}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
    return ret


def check_file_extract_bytes(fname, bytes, kwargs, func):
    ret = func(source=bytes, **kwargs)
    outfile = f"{fname}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
    return ret


def compare_params(left, right):
    lpar = left.attrs["original_metadata"].get("params", {})
    rpar = right.attrs["original_metadata"].get("params", {})
    for k in rpar:
        if k.endswith("vs.") or k.startswith("unit") or k == "I Range":
            assert k in lpar, f"Param {k!r} not found in mpt file: {lpar.keys()}"
            assert lpar[k] == rpar[k], f"Inconsistent param {k!r}: {lpar[k]}, {rpar[k]}"


@pytest.mark.parametrize(
    "froot, locale",
    [
        ("bcd.issue_241", "en_US"),
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
        ("cv.issue_217", "de_DE"),
        ("cva.issue_135", "en_US"),
        ("cva.issue_202", "en_US"),
        ("gcpl", "en_US"),
        ("gcpl.issue_149", "de_DE"),
        ("gcpl.issue_175", "en_US"),
        ("gcpl.pr_182.1", "en_US"),
        ("gcpl.pr_182.2", "en_US"),
        ("gcpl.issue_211", "en_US"),
        ("gcpl.issue_226.I", "en_US"),
        ("gcpl.issue_226.CxN", "en_US"),
        ("gcpl.issue_228", "en_US"),
        ("gcpl.issue_230", "en_US"),
        ("geis", "en_US"),
        ("lsv", "en_US"),
        ("lsv.issue_195", "en_US"),
        ("mb", "en_US"),
        ("mb.issue_95", "en_US"),
        ("mb.issue_149", "de_DE"),
        ("mb.issue_218", "en_US"),
        ("mb.issue_223", "en_GB"),
        ("mp.issue_183", "en_US"),
        ("ocv", "en_US"),
        ("ocv.issue_149", "de_DE"),
        ("peis", "en_US"),
        ("peis.issue_225.no_ece", "en_US"),
        ("peis.issue_225.with_ece", "en_US"),
        ("peis.issue_225.ewe_ece", "en_US"),
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

        bkey = key
        if bkey not in bret:
            if key.replace("we", "") in bret:
                bkey = key.replace("we", "")
            elif key.replace("we ", "") in bret:
                bkey = key.replace("we ", "")
        assert bkey in bret

        try:
            if np.isdtype(aret[key].dtype, "numeric"):
                np.testing.assert_allclose(
                    aret[key],
                    bret[bkey],
                    equal_nan=True,
                    atol=1e-8,
                    rtol=1e-5,
                )
            else:
                np.testing.assert_array_equal(aret[key], bret[bkey])
        except AssertionError as e:
            e.args = (e.args[0] + f"\nError happened on key: {key!r}\n",)
            raise e
    compare_params(aret, bret)


@pytest.mark.parametrize(
    "froot, locale",
    [
        ("ca", "en_US"),
    ],
)
def test_eclab_consistency_extract_mpr_bytes(froot, locale, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", locale=locale, encoding="windows-1252")
    with open(f"{froot}.mpr", "rb") as mpr_file:
        mpr_bytes = mpr_file.read()
    aret = check_file_extract_bytes(f"{froot}.mpr", mpr_bytes, kwargs, extract_mpr)
    bret = check_file(f"{froot}.mpr", kwargs, extract_mpr)

    for key in aret.variables:
        try:
            xr.testing.assert_equal(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"\nError happened on key: {key!r}\n",)
            raise e
    compare_params(aret, bret)


@pytest.mark.parametrize(
    "froot, locale",
    [
        ("geis.issue_149", "en_US"),
        ("peis.issue_149", "en_US"),
    ],
)
def test_eclab_consistency_partial_149(froot, locale, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", locale=locale, encoding="windows-1252")
    aret = check_file(f"{froot}.mpr", kwargs, extract_mpr)
    bret = check_file(f"{froot}.mpt", kwargs, extract_mpt)

    for key in aret.variables:
        if key.endswith("std_err"):
            continue
        elif key in {
            "THD Ewe",
            "NSD Ewe",
            "NSR Ewe",
            "|Ewe h2|",
            "|Ewe h3|",
            "|Ewe h4|",
            "|Ewe h5|",
            "|Ewe h6|",
            "|Ewe h7|",
            "THD I",
            "NSD I",
            "NSR I",
            "|I h2|",
            "|I h3|",
            "|I h4|",
            "|I h5|",
            "|I h6|",
            "|I h7|",
        }:
            continue

        bkey = key
        if bkey not in bret:
            if key.replace("we", "") in bret:
                bkey = key.replace("we", "")
            elif key.replace("we ", "") in bret:
                bkey = key.replace("we ", "")

        assert bkey in bret

        try:
            if np.isdtype(aret[key].dtype, "numeric"):
                np.testing.assert_allclose(
                    aret[key],
                    bret[bkey],
                    equal_nan=True,
                    atol=1e-8,
                    rtol=1e-5,
                )
            else:
                np.testing.assert_array_equal(aret[key], bret[bkey])
        except AssertionError as e:
            e.args = (e.args[0] + f"\nError happened on key: {key!r}\n",)
            raise e
    compare_params(aret, bret)


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("mb.issue_95.mpt", "mb.issue_95.de.mpt"),
    ],
)
def test_eclab_mpt_locale(afile, bfile, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", encoding="windows-1252")
    aret = extract_mpt(source=Path(afile), locale="en_US", **kwargs)
    bret = extract_mpt(source=Path(bfile), locale="de_DE", **kwargs)
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
    aret = extract_mpt(source=Path(afile), locale="en_US", **kwargs)
    bret = extract_mpt(source=Path(bfile), locale="en_US", **kwargs)

    for key in aret.variables:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            if key in {"Efficiency", "Efficiency_std_err"}:
                pass
            else:
                e.args = (e.args[0] + f"\nError happened on key: {key!r}\n",)
                raise e
