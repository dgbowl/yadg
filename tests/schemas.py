dummy_1 = {"datagram": "dummy","import": {"folders": ["."], "suffix": "wrong"}}
dummy_2 = {"datagram": "dummy", "import": {"paths": ["dummy_schema_2.json"]}}
dummy_3 = {"datagram": "dummy", "import": {"folders": ["."], "contains": "schema"}}
dummy_4 = {"datagram": "dummy", "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]}}
dummy_5 = {"datagram": "dummy", "import": {"folders": ["."], "prefix": "dummy", "contains": "1"}}

gctrace_chromtab = {
    "det":  {
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
    },
    "sp":   {
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
}