from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    dg_get_quantity,
    compare_result_dicts,
)


def test_datagram_from_meascsv(datadir):
    input = {
        "case": "data_3.1.0/00-experiment/measurement.csv",
        "parameters": {},
    }
    ret = datagram_from_input(input, "meascsv", datadir)
    standard_datagram_test(ret, {"nsteps": 1, "step": 0, "nrows": 1662, "point": 0})

    val = dg_get_quantity(ret, step="0", col="T_f", utsrow=0)
    compare_result_dicts(val, {"n": 20.9, "s": 0.1, "u": "degC"})

    val = dg_get_quantity(ret, step=0, col="T_f", utsrow=100)
    compare_result_dicts(val, {"n": 455.1, "s": 0.1, "u": "degC"})
