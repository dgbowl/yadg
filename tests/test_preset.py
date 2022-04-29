import pytest
import os
import json
from tests.utils import standard_datagram_test
from dgbowl_schemas.yadg_dataschema import DataSchema

import yadg.dgutils
import yadg.core


@pytest.mark.parametrize(
    "input, ts",
    [
        ("data_1", {"nsteps": 2, "step": 0, "nrows": 1662}),
        ("data_2", {"nsteps": 2, "step": 0, "nrows": 2}),
    ],
)
def test_preset(input, ts, datadir):
    os.chdir(datadir)

    with open(f"{input}.preset.json") as infile:
        preset = json.load(infile)

    schema = yadg.dgutils.schema_from_preset(preset, input)
    ds = DataSchema(**schema)

    ret = yadg.core.process_schema(ds)
    standard_datagram_test(ret, ts)
