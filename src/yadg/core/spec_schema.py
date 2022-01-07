schema_version = "4.0.rc1"

calib = {
    "type": dict,
    "one": {
        "linear": {
            "type": dict,
            "any": {"slope": {"type": float}, "intercept": {"type": float}},
        },
        "inverse": {
            "type": dict,
            "any": {"slope": {"type": float}, "intercept": {"type": float}},
        },
        "poly": {"type": dict, "each": {"type": float}},
        "polynomial": {"type": dict, "each": {"type": float}},
    },
    "any": {
        "atol": {"type": float},
        "rtol": {"type": float},
        "forcezero": {"type": bool},
    },
}

peakdetect = {
    "type": dict,
    "any": {
        "window": {"type": int},
        "polyorder": {"type": int},
        "prominence": {"type": float},
        "threshold": {"type": float},
    },
}

detectors = {
    "type": dict,
    "each": {
        "type": dict,
        "all": {"id": {"type": int}, "peakdetect": peakdetect},
        "any": {"prefer": {"type": bool}},
    },
}

species = {
    "type": dict,
    "each": {
        "type": dict,
        "each": {
            "type": dict,
            "all": {"l": {"type": float}, "r": {"type": float}},
            "any": {"calib": calib},
        },
    },
}

convert = {
    "type": dict,
    "each": {
        "type": dict,
        "each": {"type": dict, "any": {"calib": calib, "fraction": {"type": float}}},
        "any": {"unit": {"type": str}},
    },
}

schema_step = {
    "type": dict,
    "all": {
        "parser": {
            "type": str,
            "one": [
                "dummy",
                "basiccsv",
                "chromtrace",
                "qftrace",
                "flowdata",
                "meascsv",
                "electrochem",
                "masstrace",
            ],
        },
        "import": {
            "type": dict,
            "one": {"files": {"type": list}, "folders": {"type": list}},
            "any": {
                "prefix": {"type": str},
                "suffix": {"type": str},
                "contains": {"type": str},
                "encoding": {"type": str},
            },
        },
    },
    "any": {
        "tag": {"type": str},
        "export": {"type": str},
        "parameters": {"type": dict, "any": {}, "allow": True},
    },
}

timestamp = {"type": dict, "any": {"index": {"type": int}, "format": {"type": str}}}

# general parameters
schema_step["any"]["parameters"]["any"].update(
    {
        "atol": {"type": float},
        "rtol": {"type": float},
        "sigma": {
            "type": dict,
            "each": {
                "type": dict,
                "any": {"atol": {"type": float}, "rtol": {"type": float}},
            },
        },
        "calfile": {"type": str},
    }
)

# basiccsv parameters
schema_step["any"]["parameters"]["any"].update(
    {
        "sep": {"type": str},
        "units": {"type": dict, "each": {"type": str}},
        "timestamp": {
            "type": dict,
            "any": {
                "timestamp": timestamp,
                "uts": timestamp,
                "date": timestamp,
                "time": timestamp,
            },
        },
        "convert": convert,
    }
)

# chromtrace parameters
schema_step["any"]["parameters"]["any"].update(
    {
        "tracetype": {
            "type": str,
            "one": [],
        },
        "species": species,
        "detectors": detectors,
    }
)
schema_step["any"]["parameters"]["any"]["tracetype"]["one"].append("ezchrom.asc")
schema_step["any"]["parameters"]["any"]["tracetype"]["one"].append("fusion.json")
schema_step["any"]["parameters"]["any"]["tracetype"]["one"].append("agilent.ch")
schema_step["any"]["parameters"]["any"]["tracetype"]["one"].append("agilent.dx")
schema_step["any"]["parameters"]["any"]["tracetype"]["one"].append("agilent.csv")

# qftrace parameters
schema_step["any"]["parameters"]["any"].update(
    {
        "method": {"type": str, "one": ["naive", "lorentz", "kajfez"]},
        "height": {"type": float},
        "distance": {"type": float},
        "cutoff": {"type": float},
        "threshold": {"type": float},
    }
)
schema_step["any"]["parameters"]["any"]["tracetype"]["one"].append("labview.csv")

# masstrace parameters
schema_step["any"]["parameters"]["any"]["tracetype"]["one"].append("quadstar.sac")

# flowdata parameters
schema_step["any"]["parameters"]["any"].update(
    {
        "date": {"type": str},
        "filetype": {
            "type": str,
            "one": [],
        },
    }
)
schema_step["any"]["parameters"]["any"]["filetype"]["one"].append("drycal")

schema = {
    "type": dict,
    "all": {
        "metadata": {
            "type": dict,
            "all": {
                "provenance": {"type": (dict, str)},
                "schema_version": {"type": str},
            },
            "any": {"timezone": {"type": str}},
        },
        "steps": {"type": list, "each": schema_step},
    },
}

# electrochem parameters
schema_step["any"]["parameters"]["any"]["filetype"]["one"].append("eclab.mpt")
schema_step["any"]["parameters"]["any"]["filetype"]["one"].append("eclab.mpr")
