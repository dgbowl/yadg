calib = {
    "type": dict,
    "one": {
        "linear": {
            "type": dict, 
            "any": {"slope": {"type": float}, "intercept": {"type": float}}
        },
        "inverse": {
            "type": dict, 
            "any": {"slope": {"type": float}, "intercept": {"type": float}}
        },
        "poly": {"type": dict, "each": {"type": float}},
        "polynomial": {"type": dict, "each": {"type": float}}
    },
    "any": {"atol": {"type": float}, "rtol": {"type": float}}
}

peakdetect = {
    "type": dict,
    "any": {
        "window": {"type": int}, 
        "polyorder": {"type": int},
        "prominence": {"type": float},
        "threshold": {"type": float}
    }
}

detectors = {
    "type": dict,
    "each": {
        "type": dict,
        "all": {"id": {"type": int}, "peakdetect": peakdetect},
        "any": {"prefer": {"type": bool}}
    }
}

species = {
    "type": dict,
    "each": {
        "type": dict,
        "each": {
            "type": dict,
            "all": {"l": {"type": float}, "r": {"type": float}},
            "any": {"calib": calib}
        }
    }
}

convert = {
    "type": dict, 
    "each": {
        "type": dict, 
        "all": {"header": {"type": str}, "calib": calib},
        "any": {"unit": {"type": str}}
    }
}