import pytest
import os
import pickle
from yadg.extractors.drycal.txt import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        "20211011_DryCal_out.txt",
    ],
)
def test_drycal_txt(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile), encoding="utf8", timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    compare_datatrees(ret, ref, thislevel=True)
