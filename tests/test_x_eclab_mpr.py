import pytest
import os
import pickle
from yadg.extractors.eclab.mpr import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "ca.mpr",
        "ca.issue_134.mpr",
        "cp.mpr",
        "cp.issue_61.mpr",
        "cv.mpr",
        "cva.issue_135.mpr",
        "gcpl.mpr",
        "geis.mpr",
        "lsv.mpr",
        "mb.mpr",
        "mb.issue_95.mpr",
        "ocv.mpr",
        "peis.mpr",
        "wait.mpr",
        "zir.mpr",
        "vsp_ocv_with.mpr",
        "vsp_ocv_wo.mpr",
        "vsp_peis_with.mpr",
    ],
)
def test_eclab_mpr(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
