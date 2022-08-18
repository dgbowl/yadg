import pytest
import os
import json
import yaml
import yadg.core
from dgbowl_schemas import to_dataschema


def _schema_4_0(input, parser, version):
    if "files" in input:
        files = input["files"]
    elif "case" in input:
        files = [input["case"]]
    elif "folders" in input:
        files = None
    else:
        raise ValueError()
    schema = {
        "metadata": {
            "provenance": "datagram_from_input",
            "schema_version": version,
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
                    "folders": input.get("folders"),
                    "files": files,
                },
                "externaldate": input.get("externaldate", None),
            }
        ],
    }
    if "parameters" in input:
        schema["steps"][0]["parameters"] = input["parameters"]
    return schema


def _schema_4_1(input, parser, version):
    if "files" in input:
        files = input["files"]
    elif "case" in input:
        files = [input["case"]]
    elif "folders" in input:
        files = input["folders"]
    else:
        raise ValueError()
    schema = {
        "metadata": {
            "provenance": {"type": "datagram_from_input"},
            "version": version,
            "timezone": input.get("timezone", "UTC"),
        },
        "steps": [
            {
                "parser": parser,
                "input": {
                    "prefix": input.get("prefix", None),
                    "suffix": input.get("suffix", None),
                    "contains": input.get("contains", None),
                    "encoding": input.get("encoding", "UTF-8"),
                    "files": files,
                },
                "parameters": input.get("parameters", None),
                "externaldate": input.get("externaldate", None),
            }
        ],
    }
    return schema


def _schema_4_2(input, parser, version):
    if "files" in input:
        files = input["files"]
    elif "case" in input:
        files = [input["case"]]
    elif "folders" in input:
        files = input["folders"]
    else:
        raise ValueError()
    schema = {
        "metadata": {
            "provenance": {"type": "datagram_from_input"},
            "version": version,
            "timezone": input.get("timezone", "UTC"),
        },
        "steps": [
            {
                "parser": parser,
                "input": {
                    "prefix": input.get("prefix", None),
                    "suffix": input.get("suffix", None),
                    "contains": input.get("contains", None),
                    "encoding": input.get("encoding", "UTF-8"),
                    "files": files,
                },
                "parameters": input.get("parameters", None),
                "externaldate": input.get("externaldate", None),
            }
        ],
    }
    return schema


def datagram_from_file(infile, datadir):
    os.chdir(datadir)
    with open(infile, "r") as f:
        if infile.endswith("json"):
            schema = json.load(f)
        else:
            schema = yaml.safe_load(f)
    ds = to_dataschema(**schema)
    return yadg.core.process_schema(ds)


def datagram_from_input(input, parser, datadir, version="4.0"):
    if version in {"4.0", "4.0.0", "4.0.1"}:
        schema = _schema_4_0(input, parser, version)
    elif version in {"4.1"}:
        schema = _schema_4_1(input, parser, version)
    elif version in {"4.2"}:
        schema = _schema_4_2(input, parser, version)
    os.chdir(datadir)
    ds = to_dataschema(**schema)
    return yadg.core.process_schema(ds)


def standard_datagram_test(datagram, testspec):
    assert yadg.core.validators.validate_datagram(datagram), "datagram is invalid"
    assert len(datagram["steps"]) == testspec["nsteps"], "wrong number of steps"
    steps = datagram["steps"][testspec["step"]]["data"]
    assert len(steps) == testspec["nrows"], (
        "wrong number of timesteps in a step: "
        f"ret: {len(steps)}, ref: {testspec['nrows']}"
    )
    json.dumps(datagram)


def pars_datagram_test(datagram, testspec):
    steps = datagram["steps"][testspec["step"]]["data"]
    tstep = steps[testspec["point"]]
    for tk, tv in testspec["pars"].items():
        if tk != "uts":
            rd = "raw" if tv.get("raw", True) else "derived"
            if tk not in tstep[rd]:
                assert tv["value"] is None
            else:
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
