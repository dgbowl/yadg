import pytest
import os
import yaml
import pickle
from .utils import compare_datatrees
from yadg.core import process_schema
from dgbowl_schemas.yadg import to_dataschema


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
    with open(infile, "r") as inf:
        schema = yaml.safe_load(inf)
    ret = process_schema(to_dataschema(**schema))
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, toplevel=False)
