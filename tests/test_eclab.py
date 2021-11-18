import pytest

from tests.utils import (
    compare_result_dicts,
    datadir,
    datagram_from_input,
    pars_datagram_test,
    standard_datagram_test,
)

# Tests for the eclab module:
# TODO: Test parsers for different file versions.


@pytest.mark.parametrize(
    "input, ts",
    [
        (  # ts0 - ca.mpr, no loops, single sequence
            {"case": "ca.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 721, "point": 0, "pars": {}},
        ),
        (  # ts1 - ca.mpt, no loops, single sequence
            {"case": "ca.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 721, "point": 0, "pars": {}},
        ),
        (  # ts2 - cp.mpr, no loops, single sequence
            {"case": "cp.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 121, "point": 0, "pars": {}},
        ),
        (  # ts3 - cp.mpt, no header, INF in datapoints
            {"case": "cp.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 121, "point": 0, "pars": {}},
        ),
        (  # ts4 - cv.mpr, no loops, single sequence
            {"case": "cv.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 3692, "point": 0, "pars": {}},
        ),
        (  # ts5 - cv.mpt, no header
            {"case": "cv.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 3692, "point": 0, "pars": {}},
        ),
        (  # ts6 - gcpl.mpr, one loop, three sequences
            {"case": "gcpl.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 12057, "point": 0, "pars": {}},
        ),
        (  # ts7 - gcpl.mpt, one loop, three sequences
            {"case": "gcpl.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 12057, "point": 0, "pars": {}},
        ),
        (  # ts8 - geis.mpr, no loops, single sequence
            {"case": "geis.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 2528, "point": 0, "pars": {}},
        ),
        (  # ts9 - geis.mpt, no loops, single sequence
            {"case": "geis.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 2528, "point": 0, "pars": {}},
        ),
        (  # ts10 - lsv.mpr, no loops, single sequence
            {"case": "lsv.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 201, "point": 0, "pars": {}},
        ),
        (  # ts11 - lsv.mpt, no header
            {"case": "lsv.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 201, "point": 0, "pars": {}},
        ),
        (  # ts12 - mb.mpr, no loops, six sequences
            {"case": "mb.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 152, "point": 0, "pars": {}},
        ),
        (  # ts13 - mb.mpt, no header
            {"case": "mb.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 152, "point": 0, "pars": {}},
        ),
        (  # ts14 - ocv.mpr, no loops, single sequence
            {"case": "ocv.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 61, "point": 0, "pars": {}},
        ),
        (  # ts15 - ocv.mpt, no header
            {"case": "ocv.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 61, "point": 0, "pars": {}},
        ),
        (  # ts16 - peis.mpr, no loops, single sequence
            {"case": "peis.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 31, "point": 0, "pars": {}},
        ),
        (  # ts17 - peis.mpt, no header
            {"case": "peis.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 31, "point": 0, "pars": {}},
        ),
        (  # ts18 - wait.mpr, no loops, single sequence, no datapoints
            {"case": "wait.mpr"},
            {"nsteps": 1, "step": 0, "nrows": 0, "point": 0, "pars": {}},
        ),
        (  # ts19 - wait.mpt, no header, no datapoints
            {"case": "wait.mpt"},
            {"nsteps": 1, "step": 0, "nrows": 0, "point": 0, "pars": {}},
        ),
    ],
)
def test_datagram_from_eclab(input, ts, datadir):
    ret = datagram_from_input(input, "eclab", datadir)
    standard_datagram_test(ret, ts)
    # pars_datagram_test(ret, ts)
