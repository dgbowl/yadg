import pytest
import os
import pickle
from yadg.extractors.phi.spe import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "test0.spe",
        "test1.spe",
    ],
)
def test_phi_spe(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile)
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
