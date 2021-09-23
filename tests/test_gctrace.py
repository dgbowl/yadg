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
        "import": {"folders": [datadir], 
                   "prefix": input["prefix"],
                   "suffix": input["suffix"]},
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
        "CO2":       {"l":  3.50*60, "r":  3.77*60, "calib": {"linear": {"slope":  761.60}}},
        "ethylene":  {"l":  4.29*60, "r":  4.51*60, "calib": {"linear": {"slope":  649.69}}},
        "ethane":    {"l":  4.76*60, "r":  5.10*60, "calib": {"linear": {"slope": 1154.38}}},
        "propylene": {"l":  7.27*60, "r":  7.55*60, "calib": {"linear": {"slope": 1413.15}}},
        "propane":   {"l":  7.57*60, "r":  8.00*60, "calib": {"linear": {"slope": 1590.85}}},
        "butane":    {"l": 11.98*60, "r": 12.55*60, "calib": {"linear": {"slope": 1919.22}}},
        "O2":        {"l": 13.90*60, "r": 14.03*60, "calib": {"linear": {"slope":  890.20}}},
        "N2":        {"l": 14.05*60, "r": 14.61*60, "calib": {"linear": {"slope":  904.23}}},
        "methane":   {"l": 15.42*60, "r": 15.68*60, "calib": {"linear": {"slope":  640.75}}},
        "CO":        {"l": 16.00*60, "r": 16.34*60, "calib": {"linear": {"slope":  911.73}}}
    },
    "FID": {
        "CO":        {"l":  511.8, "r":  521.4, "calib": {"linear": {"slope": 1873.56}}},
        "methane":   {"l":  521.4, "r":  526.8, "calib": {"linear": {"slope": 1795.41}}},
        "CO2":       {"l":  529.2, "r":  538.8, "calib": {"linear": {"slope": 1841.64}}},
        "ethylene":  {"l":  541.8, "r":  550.2, "calib": {"linear": {"slope": 3565.07}}},
        "ethane":    {"l":  552.6, "r":  558.0, "calib": {"linear": {"slope": 3570.01}}},
        "propylene": {"l":  595.2, "r":  602.0, "calib": {"linear": {"slope": 5306.26}}},
        "propane":   {"l":  602.0, "r":  606.0, "calib": {"linear": {"slope": 5326.11}}},
        "butane":    {"l":  690.0, "r":  696.0, "calib": {"linear": {"slope": 7121.53}}},
        "acetic":    {"l":  249.6, "r":  260.4, "calib": {"linear": {"slope": 3565.07}}},
        "acrylic":   {"l":  307.2, "r":  318.0, "calib": {"linear": {"slope": 5306.26}}}
    }
}

gcms_chromtab = {}
gcms_chromtab["det"] = {
    "MS": {
        "id": 0,
        "peakdetect": {
            "window": 15,
            "polyorder": 5,
            "prominence": 1e5,
            "threshold": 1e2
        },
        "prefer": True
    },
    "TCD": {
        "id": 1,
        "peakdetect": {
            "window": 15,
            "polyorder": 2,
            "prominence": 1e5,
            "threshold": 1e2
        }
    },
    "FID": {
        "id": 2,
        "peakdetect": {
            "window": 15,
            "polyorder": 2,
            "prominence": 1e5,
            "threshold": 1e2
        }
    }
}
gcms_chromtab["sp"] = {
    "MS": {
        "N2":      {"l": 1.721*60, "r": 1.871*60},
        "CH3OH":   {"l": 1.871*60, "r": 1.997*60},
        "CH2O":    {"l": 2.140*60, "r": 2.195*60},
        "CH3OCHO": {"l": 2.194*60, "r": 2.254*60}
    },
    "TCD": {
        "CO2": {"l": 2.990*60, "r": 3.157*60},
        "H2":  {"l": 4.312*60, "r": 4.506*60},
        "O2":  {"l": 4.510*60, "r": 4.690*60},
        "N2":  {"l": 4.700*60, "r": 4.965*60}
    },
    "FID": {
        "CH3OH":   {"l": 1.850*60, "r": 2.140*60},
        "CH3OCHO": {"l": 2.140*60, "r": 2.628*60}
    }
}

@pytest.mark.parametrize("input, ts", [
    ({"prefix": "2019-12-03", "suffix": "dat.asc", 
      "parameters": {"tracetype": "datasc", "species": gc_5890_FHI["sp"], "detectors": gc_5890_FHI["det"]},},
     {"nsteps": 1, "step": 0, "ntsteps": 3, "method": "polyarc+TCD_PK_09b.met", "xout": {"propane": 0.022, "N2": 0.915}}),  
    ({"prefix": "CHROMTAB", "suffix": "CSV", 
      "parameters": {"tracetype": "chromtab", "species": gcms_chromtab["sp"], "detectors": gcms_chromtab["det"]},},
     {"nsteps": 1, "step": 0, "ntsteps": 3, "method": "n/a", "xout": {"N2": 0.74}}),   
])
def test_datagram_from_gctrace(input, ts, datadir):
    ret = datagram_from_gctrace(input, datadir)
    assert len(ret["data"]) == ts["nsteps"]
    step = ret["data"][ts["step"]]
    assert step["metadata"]["gcparams"]["method"].endswith(ts["method"])
    assert len(step["timesteps"]) == ts["ntsteps"]
    for tstep in step["timesteps"]:
        print(tstep["xout"])
        for k, v in ts["xout"].items():
            assert tstep["xout"][k][0] == pytest.approx(v, rel = 0.02)
