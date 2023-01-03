import os
import json
from tests.utils import standard_datagram_test, compare_result_dicts

import yadg.dgutils
import yadg.core


def test_update_schema_310(datadir):
    os.chdir(datadir)
    with open("schema_3.1.0.json") as infile:
        inobj = json.load(infile)

    schema = yadg.dgutils.update_object("schema", inobj)

    ret = yadg.core.process_schema(schema)
    standard_datagram_test(ret, {"nsteps": 3, "step": 0, "nrows": 1662})

    # meascsv test
    compare_result_dicts(
        ret["steps"][0]["data"][0]["raw"]["T_f"], {"n": 20.9, "s": 0.1, "u": "degC"}
    )

    # qftrace test
    f = {
        "n": ret["steps"][1]["data"][0]["raw"]["traces"]["S11"]["f"]["n"][0],
        "s": ret["steps"][1]["data"][0]["raw"]["traces"]["S11"]["f"]["s"][0],
        "u": ret["steps"][1]["data"][0]["raw"]["traces"]["S11"]["f"]["u"],
    }
    compare_result_dicts(f, {"n": 7.1e9, "s": 1e3, "u": "Hz"})
    re = {
        "n": ret["steps"][1]["data"][0]["raw"]["traces"]["S11"]["Re(Γ)"]["n"][0],
        "s": ret["steps"][1]["data"][0]["raw"]["traces"]["S11"]["Re(Γ)"]["s"][0],
        "u": ret["steps"][1]["data"][0]["raw"]["traces"]["S11"]["Re(Γ)"]["u"],
    }
    compare_result_dicts(re, {"n": -0.0192804, "s": 1e-8, "u": " "})

    # gctrace test
    t = {
        "n": ret["steps"][2]["data"][0]["raw"]["traces"]["0"]["t"]["n"][0],
        "s": ret["steps"][2]["data"][0]["raw"]["traces"]["0"]["t"]["s"][0],
        "u": ret["steps"][2]["data"][0]["raw"]["traces"]["0"]["t"]["u"],
    }
    compare_result_dicts(t, {"n": 0.0, "s": 0.100002, "u": "s"})
    y = {
        "n": ret["steps"][2]["data"][0]["raw"]["traces"]["0"]["y"]["n"][0],
        "s": ret["steps"][2]["data"][0]["raw"]["traces"]["0"]["y"]["s"][0],
        "u": ret["steps"][2]["data"][0]["raw"]["traces"]["0"]["y"]["u"],
    }
    compare_result_dicts(y, {"n": 2.105203, "s": 0.000130, "u": "pA"})
