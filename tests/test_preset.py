import pytest
import os
import json
import yadg.dgutils
import yadg.core


def standard_datagram_test(datagram, testspec):
    assert len(datagram.children) == testspec["nsteps"], "wrong number of steps"
    if isinstance(testspec["step"], str):
        step = datagram[f"{testspec['step']}"]
    else:
        name = list(datagram.children.keys())[testspec["step"]]
        step = datagram[name]
    if len(step.children) > 0:
        for k, v in step.items():
            assert len(v["uts"]) == testspec["nrows"], (
                f"wrong number of timesteps in a child Dataset {k}: "
                f"ret: {len(v['uts'])}, ref: {testspec['nrows']}"
            )
    if "uts" in step:
        assert len(step["uts"]) == testspec["nrows"], (
            "wrong number of timesteps in a step: "
            f"ret: {len(step['uts'])}, ref: {testspec['nrows']}"
        )
    datagram.to_netcdf(".test.nc", engine="h5netcdf")


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

    schema = yadg.dgutils.update_schema(preset)
    ds = yadg.dgutils.schema_from_preset(schema, input)
    ret = yadg.core.process_schema(ds)
    standard_datagram_test(ret, ts)
