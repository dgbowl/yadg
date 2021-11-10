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
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cp.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cp.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cv.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'cv.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'gcpl.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'gcpl.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'geis.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'geis.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'lsv.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'lsv.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'mb.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'mb.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ocv.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ocv.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'peis.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'peis.mpt'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'wait.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
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
                'nsteps': 0,
                'steps': 0,
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
