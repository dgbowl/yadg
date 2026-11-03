import pytest
import os
import pickle
from yadg.extractors.yadg.json import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        "ds.4.0.dg.json",
        "ds.4.1.dg.json",
        "ds.4.2.dg.json",
    ],
)
def test_yadg_json(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile), encoding="utf-8")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    compare_datatrees(ret, ref, thislevel=True)
