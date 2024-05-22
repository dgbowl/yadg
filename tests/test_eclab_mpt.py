import pytest
import os
import pickle
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
