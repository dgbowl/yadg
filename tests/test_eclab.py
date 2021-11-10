import pytest

from tests.utils import (compare_result_dicts, datadir, datagram_from_input,
                         pars_datagram_test, standard_datagram_test)

# Tests for the eclab module:
# TODO: Test parsers for different file versions.


@pytest.mark.parametrize(
    'input, ts',
    [
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 721,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 721,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cp.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 121,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cp.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 121,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cv.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 3692,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cv.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 3692,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'gcpl.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 12057,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'gcpl.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 12057,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'geis.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 2528,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'geis.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 2528,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'lsv.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 201,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'lsv.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 201,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'mb.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 152,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'mb.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 152,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ocv.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 61,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ocv.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 61,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'peis.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 31,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'peis.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 31,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'wait.mpr'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'wait.mpt'
            },
            {
                'nsteps': 1,
                'step': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
    ],
)
def test_datagram_from_eclab(input, ts, datadir):
    ret = datagram_from_input(input, "eclab", datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)
