import pytest
import os
import pickle
import yaml
from yadg.extractors.tomato.json import extract
from .utils import compare_datatrees
from yadg.core import process_schema
from dgbowl_schemas.yadg import to_dataschema


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
    compare_datatrees(ret, ref)


def test_tomato_json_dataschema(datadir):
    os.chdir(datadir)
    with open("tomato_json_dataschema.yml", "r") as inf:
        schema = yaml.safe_load(inf)
    ret = process_schema(to_dataschema(**schema))
    outfile = "tomato_json_dataschema.yml.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, toplevel=False)
