import pytest
import os
import pickle
from yadg.extractors.agilent.dx import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "2021-11-12 12-39-18+01-00-02.dx",
    ],
)
def test_agilent_dx(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
