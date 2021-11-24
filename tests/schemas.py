dummy_1 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "suffix": "wrong"}}],
}
dummy_2 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [{"parser": "dummy", "import": {"files": ["dummy_schema_2.json"]}}],
}
dummy_3 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "contains": "schema"}}],
}
dummy_4 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
dummy_5 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"folders": ["."], "prefix": "dummy", "contains": "1"},
        }
    ],
}
fail_1 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [
        {
            "parse": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fail_2 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [
        {
            "parser": "dumm",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fail_3 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {
                "files": ["dummy_schema_1.json", "dummy_schema_2.json"],
                "folders": ["."],
            },
        }
    ],
}
fail_4 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [{"parser": "dummy", "import": {}}],
}
fail_5 = {
    "metadata": {"provenance": "manual", "schema_version": "0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
            "key": "value",
        }
    ],
}

gctrace_chromtab = {
    "det": {
        "MS": {
            "id": 0,
            "peakdetect": {
                "window": 1,
                "polyorder": 2,
                "prominence": 1e5,
                "threshold": 1.0,
            },
            "prefer": True,
        },
        "TCD": {
            "id": 1,
            "peakdetect": {
                "window": 1,
                "polyorder": 2,
                "prominence": 1e5,
                "threshold": 1.0,
            },
        },
        "FID": {
            "id": 2,
            "peakdetect": {
                "window": 1,
                "polyorder": 2,
                "prominence": 1e5,
                "threshold": 1.0,
            },
        },
    },
    "sp": {
        "MS": {
            "N2": {
                "l": 1.721 * 60,
                "r": 1.871 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
            "CH3OH": {
                "l": 1.871 * 60,
                "r": 1.997 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
            "CH2O": {
                "l": 2.140 * 60,
                "r": 2.195 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
            "CH3OCHO": {
                "l": 2.194 * 60,
                "r": 2.254 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
        },
        "TCD": {
            "CO2": {
                "l": 2.990 * 60,
                "r": 3.157 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
            "H2": {
                "l": 4.312 * 60,
                "r": 4.506 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
            "O2": {
                "l": 4.510 * 60,
                "r": 4.690 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
            "N2": {
                "l": 4.700 * 60,
                "r": 4.965 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
        },
        "FID": {
            "CH3OH": {
                "l": 1.850 * 60,
                "r": 2.140 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
            "CH3OCHO": {
                "l": 2.140 * 60,
                "r": 2.628 * 60,
                "calib": {"linear": {"slope": 1.0}},
            },
        },
    },
}
