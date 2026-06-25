import pytest
import os
import pickle
from yadg.extractors.yadg.json import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        #"ds.4.2.dg.json",
        "2019-09-30-30624-propane-01.datagram.json",
    ],
)
def test_yadg_json(infile, datadir):
    os.chdir(datadir)
    ret = extract(
        source=Path(infile),
        encoding="utf-8",
    )
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
