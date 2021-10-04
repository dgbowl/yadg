from .partial_specs import convert, species, detectors

spec = {
    "type": dict,
    "all": {
        "parser": {"type": str, "one": ["dummy", "basiccsv", "qftrace", "gctrace"] },
        "import": {
            "type": dict,
            "one": {"files": {"type": list}, "folders": {"type": list}},
            "any": {"prefix": {"type": str}, "suffix": {"type": str}, "contains": {"type": str}}
        }
    },
    "any": {
        "tag": {"type": str},
        "export": {"type": str},
        "parameters": {
            "type": dict,
            "any": {},
            "allow": True
        }
    }
}

# general parameters
spec["any"]["parameters"]["any"].update({
    "atol": {"type": float},
    "rtol": {"type": float},
    "sigma": {
        "type": dict, 
        "each": {
            "type": dict, 
            "any": {"atol": {"type": float}, "rtol": {"type": float}}
        }
    }
})

# basiccsv parameters
spec["any"]["parameters"]["any"].update({
    "sep": {"type": str},
    "units": {"type": dict, "each": {"type": str}},
    "timestamp": {"type": dict},
    "convert": convert
})

# gctrace parameters
spec["any"]["parameters"]["any"].update({
    "tracetype": {"type": str, "one": ["datasc", "chromtab", "fusion"]},
    "species": species,
    "detectors": detectors,
    "calfile": {"type": str}
})

# qftrace parameters
spec["any"]["parameters"]["any"].update({
    "method": {"type": str, "one": ["naive", "lorentz", "kajfez"]},
    "height": {"type": float},
    "distance": {"type": float},
    "cutoff": {"type": float},
    "threshold": {"type": float}
})