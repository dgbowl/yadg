ts0 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "suffix": "wrong"}}],
}
ts1 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"files": ["ts1.json"]}}],
}
ts2 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "contains": ".dummy."}}],
}
ts3 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
ts4 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"folders": ["."], "prefix": "ts", "contains": "1"},
        }
    ],
}
fts0 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parse": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts1 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dumm",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts2 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
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
fts3 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {}}],
}
fts4 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
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

ts5 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "input": {
                "folders": ["."],
                "suffix": "json",
                "contains": "schema",
                "exclude": "3.1.0",
            },
            "parameters": {},
        }
    ],
}

fts5 = {
    "metadata": {"provenance": "wrong", "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts6 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.0"},
    "steps": [
        {
            "parser": "dummy",
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts7 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts8 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
            "parameters": {"k": "v"},
        }
    ],
}
