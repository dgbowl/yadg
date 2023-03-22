from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
)

from uncertainties import ufloat
import pint
import datatree
from typing import Union


def dg_get_quantity(
    dt: datatree.DataTree,
    step: Union[str, int],
    col: str,
    row: int,
) -> pint.Quantity:
    if isinstance(step, str):
        step = dt[step]
    else:
        name = list(dt.children.keys())[step]
        step = dt[name]

    n = step[col][row]
    u = step[col].attrs.get("units", None)
    if step["_devs"][col].size > 1:
        d = step["_devs"][col][row]
    else:
        d = step["_devs"][col]
    return pint.Quantity(ufloat(n, d), u)


def test_datagram_from_meascsv(datadir):
    input = {
        "case": "data_3.1.0/00-experiment/measurement.csv",
        "parameters": {},
    }
    ret = datagram_from_input(input, "meascsv", datadir)
    standard_datagram_test(ret, {"nsteps": 1, "step": 0, "nrows": 1662, "point": 0})

    val = dg_get_quantity(ret, step="0", col="T_f", row=0)
    assert val.m.n == 20.9
    assert val.m.s == 0.1
    assert val.u == pint.Unit("degC")

    val = dg_get_quantity(ret, step=0, col="T_f", row=100)
    assert val.m.n == 455.1
    assert val.m.s == 0.1
    assert val.u == pint.Unit("degC")
