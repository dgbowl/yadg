import pytest
import os
import pickle
from yadg.extractors.fhimcpt.vna import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        "2019-12-03-09-01-24.csv",
        "2019-12-03-10-00-06.csv",
    ],
)
def test_fhimcpt_vna(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile), encoding="utf8")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ref=}")
    compare_datatrees(ret, ref, thislevel=True)
