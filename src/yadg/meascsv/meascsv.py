from ..helpers import *
import json

def _inferCalibration(**kwargs):
    calibkeys = ["Tcal", "Tcalfile", "MFCcal", "MFCcalfile"]
    if len(set(calibkeys) & set(kwargs)) == 0:
        return False
    calib = {}
    if "Tcalfile" in kwargs:
        with open(kwargs["Tcalfile"], "r") as infile:
            calib["Tcal"] = json.load(infile)
    if "MFCcalfile" in kwargs:
        with open(kwargs["MFCcalfile"], "r") as infile:
            calib["MFCcal"] = json.load(infile)
    if "Tcal" in kwargs:
        calib["Tcal"] = kwargs["Tcal"]
    if "MFCcal" in kwargs:
        calib["MFCcal"] = kwargs["MFCcal"]
    return calib

def process(fn, **kwargs):
    results = []
    calibration = _inferCalibration(**kwargs)
    with open(fn, "r") as infile:
        lines = [i.strip() for i in infile.readlines()]
    labels = [i.strip() for i in lines.pop(0).split(";")]
    units = [i.strip() for i in lines.pop(0).split(";")]
    for line in lines:
        raw = {}
        values = [i.strip() for i in line.split(";")]
        for vi in range(len(labels)):
            if units[vi] != "":
                raw[labels[vi]] = float(values[vi])
            else:
                raw[labels[vi]] = values[vi]
        point = {"uts": dateutils.coerceDashedDate(raw["timestamp"]),
                 "raw": raw}
        if calibration:
            if "Tcal" in calibration:
                point["T"] = raw["T_f"] * calibration["Tcal"].get("slope", 1) + calibration["Tcal"].get("intercept", 0)
            if "MFCcal" in calibration:
                X = {}
                for mfc in ["N2", "O2", "alkane", "CO/CO2", "saturator"]:
                    flow = raw[mfc] * calibration["MFCcal"].get(mfc, {}).get("slope", 1.0) + \
                                      calibration["MFCcal"].get(mfc, {}).get("intercept", 0.0) * int(raw[mfc] > 0)
                    for species, percentage in calibration["MFCcal"].get(mfc, {}).get("content", {mfc: 1.0}).items():
                        X[species] = X.get(species, 0.0) + percentage * flow
                total = sum([X[species] for species in X])
                for species in X:
                    if total > 0:
                        X[species] = X[species] / total
                    else:
                        X[species] = 0
                point["x"] = X
                for mfc in ["flow low", "flow high"]:
                    flow = raw[mfc] * calibration["MFCcal"].get(mfc, {}).get("slope", 1) + \
                                      calibration["MFCcal"].get(mfc, {}).get("intercept", 0) * int(raw[mfc] > 0)
                    point["flow"] = point.get("flow", 0) + flow
        results.append(point)
    return(results)
