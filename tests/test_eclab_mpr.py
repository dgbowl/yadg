import pytest
import os
import pickle
from yadg.extractors.eclab.mpr import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "ca.mpr",
        "cp.mpr",
        "cv.mpr",
        "gcpl.mpr",
        "geis.mpr",
        "lsv.mpr",
        "mb.mpr",
        "ocv.mpr",
        "peis.mpr",
        "wait.mpr",
        "zir.mpr",
        "mb_67.mpr",
        "issue_61_Irange_65.mpr",
        "vsp_ocv_with.mpr",
        "vsp_ocv_wo.mpr",
        "vsp_peis_with.mpr",
    ],
)
def test_eclab_mpr(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, timezone="Europe/Berlin")
    outfile = f"ref.{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref)
