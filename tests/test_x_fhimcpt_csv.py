import pytest
import os
import pickle
from yadg.extractors.fhimcpt.csv import extract
from dgbowl_schemas.yadg.dataschema_5_1.filetype import FHI_csv
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "measurement.csv",
    ],
)
def test_fhimcpt_csv(infile, datadir):
    os.chdir(datadir)
    ret = extract(
        fn=infile,
        parameters=FHI_csv(filetype="fhimcpt.csv", parameters={}).parameters,
        encoding="utf8",
        locale="en_GB",
        timezone="Europe/Berlin",
    )
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
