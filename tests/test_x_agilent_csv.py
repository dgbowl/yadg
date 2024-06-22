import pytest
import os
import pickle
from yadg.extractors.agilent.csv import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "CHROMTAB.CSV",
    ],
)
def test_agilent_csv(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, encoding="utf-8", timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
