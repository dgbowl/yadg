import pytest
from utils import (
    datagram_from_input,
    standard_datagram_test,
    pars_datagram_test,
    datadir,
)


def test_datagram_from_meascsv(datadir):
    input = {"case": "measurement.csv", "parameters": {"calfile": "fhi_tfcal.json"}}
    ret = datagram_from_input(input, "meascsv", datadir)
    standard_datagram_test(ret, {"nsteps": 1, "step": 0, "nrows": 1662, "point": 0})

    assert ret["steps"][0]["data"][0]["raw"]["T_f"] == {
        "n": 20.9,
        "s": 0.1,
        "u": "C",
    }
    assert ret["steps"][0]["data"][100]["raw"]["T_f"] == {
        "n": 455.1,
        "s": 0.1,
        "u": "C",
    }

    assert ret["steps"][0]["data"][0]["derived"]["T"] == {
        "n": 28.31537744,
        "s": 1.0,
        "u": "C",
    }
    assert ret["steps"][0]["data"][100]["derived"]["T"] == {
        "n": 403.79573256000003,
        "s": 8.075914651200002,
        "u": "C",
    }

    assert ret["steps"][0]["data"][0]["derived"]["flow"] == {
        "n": 2.1717380090210003,
        "s": 0.011003548157162944,
        "u": "ml/min",
    }
    assert ret["steps"][0]["data"][100]["derived"]["flow"] == {
        "n": 0.59405490387,
        "s": 0.010056944582182975,
        "u": "ml/min",
    }

    assert ret["steps"][0]["data"][0]["derived"]["xin"] == {
        "C3H8": {"n": 0.0, "s": 6.261885929993156e-05, "u": "-"},
        "N2": {"n": 0.9505747016707102, "s": 0.0003310858940362529, "u": "-"},
        "O2": {"n": 0.04942529832928978, "s": 0.0003257059300865775, "u": "-"},
    }
    assert ret["steps"][0]["data"][100]["derived"]["xin"] == {
        "C3H8": {"n": 0.030167329556712818, "s": 4.0227777476780384e-05, "u": "-"},
        "N2": {"n": 0.8802434898701875, "s": 0.0002461504600964663, "u": "-"},
        "O2": {"n": 0.08958918057309971, "s": 0.00025062700132648993, "u": "-"},
    }
