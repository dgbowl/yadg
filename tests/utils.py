import pytest
import os
import json
import yadg.core
from dgbowl_schemas.yadg_dataschema import DataSchema


def datagram_from_input(input, parser, datadir):
    schema = {
        "metadata": {
            "provenance": "manual",
            "schema_version": "0.1",
            "timezone": input.get("timezone", "UTC"),
        },
        "steps": [
            {
                "parser": parser,
                "import": {
                    "prefix": input.get("prefix", ""),
                    "suffix": input.get("suffix", ""),
                    "contains": input.get("contains", ""),
                    "encoding": input.get("encoding", "utf-8"),
                },
                "parameters": input.get("parameters", {}),
            }
        ],
    }
    if "externaldate" in input:
        schema["steps"][0]["externaldate"] = input["externaldate"]
    if "case" in input:
        schema["steps"][0]["import"]["files"] = [input["case"]]
    elif "files" in input:
        schema["steps"][0]["import"]["files"] = input["files"]
    elif "folders" in input:
        schema["steps"][0]["import"]["folders"] = input["folders"]
    os.chdir(datadir)
    ds = DataSchema(**schema)
    return yadg.core.process_schema(ds)


def standard_datagram_test(datagram, testspec):
    assert yadg.core.validators.validate_datagram(datagram), "datagram is invalid"
    assert len(datagram["steps"]) == testspec["nsteps"], "wrong number of steps"
    steps = datagram["steps"][testspec["step"]]["data"]
    assert len(steps) == testspec["nrows"], "wrong number of timesteps in a step"
    json.dumps(datagram)


def pars_datagram_test(datagram, testspec):
    steps = datagram["steps"][testspec["step"]]["data"]
    tstep = steps[testspec["point"]]
    for tk, tv in testspec["pars"].items():
        if tk != "uts":
            rd = "raw" if tv.get("raw", True) else "derived"
            assert (
                len(tstep[rd][tk].keys()) == 3
            ), "value not in [val, dev, unit] format"
            compare_result_dicts(
                tstep[rd][tk],
                {"n": tv["value"], "s": tv["sigma"], "u": tv["unit"]},
            )
        else:
            assert tstep[tk] == tv["value"], "wrong uts"


def compare_result_dicts(result, reference, atol=1e-6):
    assert result["n"] == pytest.approx(reference["n"], abs=atol)
    assert result["s"] == pytest.approx(reference["s"], abs=atol)
    assert result["u"] == reference["u"]
