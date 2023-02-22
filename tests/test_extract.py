import pytest
import os
import json
import pandas as pd
from yadg.extractors import extract


@pytest.mark.parametrize(
    "filetype, infile, outfile",
    [
        ("marda:biologic-mpr", "cp.mpr", "ref.cp.mpr.json"),
        ("marda:biologic-mpt", "cp.mpt", "ref.cp.mpt.json"),
    ],
)
def test_extract_marda(filetype, infile, outfile, datadir):
    os.chdir(datadir)
    ret = extract(filetype=filetype, path=infile, as_dict=False)

    with open(outfile, "r") as inf:
        ref = json.load(inf)

    assert ret["content"]["units"] == ref["content"]["units"]
    for table in {"values", "sigmas"}:
        rtab = pd.DataFrame.from_dict(ref["content"][table], orient="tight")
        assert rtab.equals(ret["content"][table])
