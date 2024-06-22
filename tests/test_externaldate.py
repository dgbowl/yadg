import pytest
import os
import pickle
from .utils import compare_datatrees, datagram_from_file


@pytest.mark.parametrize(
    "infile,",
    (
        "ts0.yml",
        "ts1.yml",
        "ts2.yml",
        "ts3.yml",
        "ts4.yml",
        "ts5.yml",
        "ts6.yml",
    ),
)
def test_externaldate_dataschema(infile, datadir):
    os.chdir(datadir)
    ret = datagram_from_file(infile)
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref)
