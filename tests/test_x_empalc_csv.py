import pytest
import os
import pickle
from yadg.extractors.empalc.csv import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        "Cu-20p_v2.csv",
        "Cu-25p_v2.csv",
    ],
)
def test_empalc_csv(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile), encoding="utf-8")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    compare_datatrees(ret, ref, thislevel=True)
