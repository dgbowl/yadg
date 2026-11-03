import pytest
import os
import pickle
from yadg.extractors.agilent.csv import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        "CHROMTAB.CSV",
    ],
)
def test_agilent_csv(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile), encoding="utf-8", timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    compare_datatrees(ret, ref, thislevel=True, descend=True)
