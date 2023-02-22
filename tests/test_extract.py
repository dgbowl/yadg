import pytest
import os
from pathlib import Path
import pandas as pd
from yadg.extractors import extract, load_json


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

    ref = load_json(Path(outfile))

    assert ret["content"]["units"] == ref["content"]["units"]
    for table in {"values", "sigmas"}:
        assert ref["content"][table].equals(ret["content"][table])
