import pytest
import os
import json
from distutils import dir_util
import datetime

from yadg import core

# tests for the basiccsv module:
#  - test_datagram_from_qftrace:
#    - tests processing using the "naive", "lorentz", and "kajfez" fitters
#    - tests passing "cutoff" parameter to the "kajfez" fitter
#    - tests passing "threshold" parameter to "naive" fitter

@pytest.fixture
def datadir(tmpdir, request):
    """
    from: https://stackoverflow.com/a/29631801
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))
    return tmpdir

def datagram_from_gctrace(input, datadir):
    schema = [{
        "datagram": "gctrace",
        "import": {"folders": [datadir], "suffix": "dat.asc"},
        "parameters": input.get("parameters", {})
    }]
    core.schema_validator(schema)
    return core.process_schema(schema)

gc_5890_FHI = {}
gc_5890_FHI["det"] = {
    "TCD": {
        "id": 1,
        "peakdetect": {
            "window": 3,
            "polyorder": 2,
            "prominence": 0.3
        }
    },
    "FID": {
        "id": 0,
        "peakdetect": {
            "window": 7,
            "polyorder": 5,
            "prominence": 2e-2
        },
        "prefer": True
    }
}
gc_5890_FHI["sp"] = {
    "TCD": {
        "CO2":       {"l":  3.50*60, "r":  3.77*60, "rf": 761.60},
        "ethylene":  {"l":  4.29*60, "r":  4.51*60, "rf": 649.69},
        "ethane":    {"l":  4.76*60, "r":  5.10*60, "rf": 1154.38},
        "propylene": {"l":  7.27*60, "r":  7.55*60, "rf": 1413.15},
        "propane":   {"l":  7.57*60, "r":  8.00*60, "rf": 1590.85},
        "butane":    {"l": 11.98*60, "r": 12.55*60, "rf": 1919.22},
        "O2":        {"l": 13.90*60, "r": 14.03*60, "rf": 890.20},
        "N2":        {"l": 14.05*60, "r": 14.61*60, "rf": 904.23},
        "methane":   {"l": 15.42*60, "r": 15.68*60, "rf": 640.75},
        "CO":        {"l": 16.00*60, "r": 16.34*60, "rf": 911.73}
    },
    "FID": {
        "CO":        {"l":  8.53*60, "r":  8.69*60, "rf": 1873.56},
        "methane":   {"l":  8.69*60, "r":  8.78*60, "rf": 1795.41},
        "CO2":       {"l":  8.82*60, "r":  8.98*60, "rf": 1841.64},
        "ethylene":  {"l":  9.03*60, "r":  9.17*60, "rf": 3565.07},
        "ethane":    {"l":  9.21*60, "r":  9.30*60, "rf": 3570.01},
        "propylene": {"l":  9.92*60, "r":  9.99*60, "rf": 5306.26},
        "propane":   {"l":  9.99*60, "r": 10.13*60, "rf": 5326.11},
        "butane":    {"l": 11.50*60, "r": 11.60*60, "rf": 7121.53},
        "acetic":    {"l":  4.16*60, "r":  4.34*60, "rf": 3565.07},
        "acrylic":   {"l":  5.12*60, "r":  5.30*60, "rf": 5306.26}
    }
}

@pytest.mark.parametrize("input, ts", [
    ({"parameters": {"tracetype": "datasc", "species": gc_5890_FHI["sp"], "detectors": gc_5890_FHI["det"]}},
     {}),  
])
def test_datagram_from_gctrace(input, ts, datadir):
    print("test input")
    print(input)
    ret = datagram_from_gctrace(input, datadir)
    print(ret)
    assert False
