import pytest
import os
import pickle
from yadg.extractors.tomato.json import extract
from .utils import compare_datatrees, datagram_from_file


@pytest.mark.parametrize(
    "infile",
    [
        "MPG2_2022-04-20T213025.275348+0000_data.json",
        "MPG2_2022-04-20T214430.234496+0000_data.json",
    ],
)
def test_tomato_json(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile)
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)


@pytest.mark.parametrize(
    "infile",
    [
        "tomato_json_dataschema.1.yml",
        "tomato_json_dataschema.2.yml",
    ],
)
def test_tomato_json_dataschema(infile, datadir):
    os.chdir(datadir)
    ret = datagram_from_file(infile)
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref)
