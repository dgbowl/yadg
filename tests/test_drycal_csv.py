import pytest
import os
import pickle
from yadg.extractors.drycal.csv import extract
import xarray as xr
import yaml
from yadg.core import process_schema
from dgbowl_schemas.yadg import to_dataschema


@pytest.mark.parametrize(
    "infile",
    [
        "20211011_DryCal_out.csv",
        "20220721-porosity-study-20p-Cu-200mA-EDLC-01-flow.csv",
        "20220912_Defender.csv",
    ],
)
def test_drycal_csv(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, encoding="utf8", timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    xr.testing.assert_identical(ret, ref)


def test_drycal_lock_stock_dataschema(datadir):
    os.chdir(datadir)
    with open("lock_stock_dataschema.yml", "r") as inf:
        schema = yaml.safe_load(inf)
    ret = process_schema(to_dataschema(**schema))
    print(f"{ret=}")
    assert ret["outlet"]["DryCal"].shape == (187,)
