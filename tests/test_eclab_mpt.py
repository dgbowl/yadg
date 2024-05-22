import pytest
import os
import pickle
import numpy as np
from yadg.extractors.eclab.mpt import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "ca.mpt",
        "cp.mpt",
        "cv.mpt",
        "gcpl.mpt",
        "geis.mpt",
        "lsv.mpt",
        "mb.mpt",
        "ocv.mpt",
        "peis.mpt",
        "wait.mpt",
        "zir.mpt",
        "mb_67.mpt",
        "issue_61_Irange_65.mpt",
        "vsp_ocv_with.mpt",
        "vsp_ocv_wo.mpt",
        "vsp_peis_with.mpt",
    ],
)
def test_eclab_mpt(infile, datadir):
    os.chdir(datadir)
    ret = extract(
        fn=infile,
        timezone="Europe/Berlin",
        encoding="windows-1252",
        locale="en_US",
    )
    outfile = f"ref.{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref)


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("mb_67.mpt", "mb_67.de.mpt"),
    ],
)
def test_eclab_mpt_locale(afile, bfile, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", encoding="windows-1252")
    aret = extract(fn=afile, locale="en_US", **kwargs)
    bret = extract(fn=bfile, locale="de_DE", **kwargs)
    compare_datatrees(aret, bret)


@pytest.mark.xfail(strict=False)
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
            if aret[key].dtype.kind in {"U"}:
                np.testing.assert_array_equal(aret[key], bret[key])
            else:
                np.testing.assert_allclose(aret[key], bret[key], rtol=1e-3, atol=1e-11)
            assert aret[key].attrs == bret[key].attrs
        except AssertionError as e:
            print(f"{key=}")
            if key.endswith("_std_err"):
                continue
            else:
                raise e
