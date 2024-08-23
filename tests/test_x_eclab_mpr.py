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
        "ca.issue_149.mpr",
        "cp.mpr",
        "cp.issue_61.mpr",
        "cp.issue_149.mpr",
        "cv.mpr",
        "cv.issue_149.mpr",
        "cva.issue_135.mpr",
        "gcpl.mpr",
        "gcpl.issue_149.mpr",
        "gcpl.issue_175.mpr",
        "geis.mpr",
        "geis.issue_149.mpr",
        "lsv.mpr",
        "mb.mpr",
        "mb.issue_95.mpr",
        "mb.issue_149.mpr",
        "ocv.mpr",
        "ocv.issue_149.mpr",
        "peis.mpr",
        "peis.issue_149.mpr",
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
    print(f"{ret=}")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
