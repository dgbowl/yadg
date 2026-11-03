import pytest
import os
import pickle
from yadg.extractors.phi.spe import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        "test0.spe",
        "test1.spe",
    ],
)
def test_phi_spe(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile))
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    compare_datatrees(ret, ref, thislevel=True)
