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
    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["T"],
        {"n": 27.1976616, "s": 0.0914933, "u": "degC"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["flow"],
        {"n": 2.1717380, "s": 0.0110035, "u": "ml/min"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["xin"]["C3H8"],
        {"n": 0.0, "s": 0.0000626, "u": " "},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["xin"]["N2"],
        {"n": 0.9505747, "s": 0.0003311, "u": " "},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["xin"]["O2"],
        {"n": 0.0494253, "s": 0.0003257, "u": " "},
    )

    # qftrace test
    compare_result_dicts(
        ret["steps"][1]["data"][0]["derived"]["S11"]["Q"],
        {"n": [3060.4456994, 1546.0093196], "s": [18.1552741, 18.3307637], "u": " "},
    )
    compare_result_dicts(
        ret["steps"][1]["data"][0]["derived"]["S11"]["f"],
        {"n": [7173122961.931216, 7348299014.344608], "s": [1000.0, 1000.0], "u": "Hz"},
    )

    # gctrace test
    compare_result_dicts(
        ret["steps"][2]["data"][0]["derived"]["xout"]["O2"],
        {"n": 0.0298672, "s": 0.0006050, "u": " "},
    )
    compare_result_dicts(
        ret["steps"][2]["data"][0]["derived"]["xout"]["N2"],
        {"n": 0.9172920, "s": 0.0007279, "u": " "},
    )
    compare_result_dicts(
        ret["steps"][2]["data"][0]["derived"]["xout"]["propane"],
        {"n": 0.0159712, "s": 0.0000442, "u": " "},
    )
    compare_result_dicts(
        ret["steps"][2]["data"][0]["derived"]["xout"]["CO2"],
        {"n": 0.0080323, "s": 0.0000520, "u": " "},
    )
    compare_result_dicts(
        ret["steps"][2]["data"][0]["derived"]["xout"]["CO"],
        {"n": 0.0288312, "s": 0.0004395, "u": " "},
    )
