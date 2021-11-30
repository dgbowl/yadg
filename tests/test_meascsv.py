import pytest
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    datadir,
    compare_result_dicts,
)


def test_datagram_from_meascsv(datadir):
    input = {
        "case": "data_3.1.0/00-experiment/measurement.csv", 
        "parameters": {"calfile": "calibrations/fhi_tfcal.json"}
    }
    ret = datagram_from_input(input, "meascsv", datadir)
    standard_datagram_test(ret, {"nsteps": 1, "step": 0, "nrows": 1662, "point": 0})

    compare_result_dicts(
        ret["steps"][0]["data"][0]["raw"]["T_f"],
        {"n": 20.9, "s": 0.1, "u": "C"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][100]["raw"]["T_f"],
        {"n": 455.1, "s": 0.1, "u": "C"},
    )

    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["T"],
        {"n": 28.3153774, "s": 1.0, "u": "C"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][100]["derived"]["T"],
        {"n": 403.7957326, "s": 8.0759147, "u": "C"},
    )

    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["flow"],
        {"n": 2.1717380, "s": 0.0110035, "u": "ml/min"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][100]["derived"]["flow"],
        {"n": 0.5940549, "s": 0.0100569, "u": "ml/min"},
    )

    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["xin"]["C3H8"],
        {"n": 0.0, "s": 0.0000626, "u": "-"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["xin"]["N2"],
        {"n": 0.9505747, "s": 0.0003311, "u": "-"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][0]["derived"]["xin"]["O2"],
        {"n": 0.0494253, "s": 0.0003257, "u": "-"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][100]["derived"]["xin"]["C3H8"],
        {"n": 0.0301673, "s": 0.0000402, "u": "-"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][100]["derived"]["xin"]["N2"],
        {"n": 0.8802435, "s": 0.0002461, "u": "-"},
    )
    compare_result_dicts(
        ret["steps"][0]["data"][100]["derived"]["xin"]["O2"],
        {"n": 0.0895892, "s": 0.0002506, "u": "-"},
    )
