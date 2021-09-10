import datetime
import json
import numpy as np
#from helpers import *

_VERSION = 0.1

def _computeWeights(n, tasktype):
    ones = [1] * n
    oneminus = [-1] + [1] * (n-1)
    if tasktype == "average":
        return ones, ones
    if tasktype == "sum":
        return ones, [1]
    if tasktype == "diff":
        return oneminus, [1]

def process(fn, **kwargs):
    with open(fn, "r") as infile:
        injson = json.load(infile)
    assert injson["meta"]["datagram"] in ["gcasc","merge"], f"Incorrect datagram passed into gcsum: {injson['meta']['datagram']}"
    checkarray = []
    for datapoint in injson["data"]:
        checkarray.append([
                           datapoint["version"], 
                           len(datapoint["detector"]), 
                           [[dd["samplerate"], dd["points"], dd["xmult"], dd["units"]] for dd in datapoint["detector"]]
                          ])
    for check in checkarray:
        assert check == checkarray[0], f'Inconsistent gcasc data passed into gcsum: {checkarray.index(check)}'
    params = kwargs.pop("pars", {})
    weights, divs = _computeWeights(len(checkarray), params.get("type", "average"))
    xs = []
    ys = []
    for det in range(len(injson["data"][0]["detector"])):
        xs.append([0]*injson["data"][0]["detector"][det]["points"])
        ys.append([0]*injson["data"][0]["detector"][det]["points"])
    data = {
            "detector": [],
            "timestamps": [each["timestamp"] for each in injson["data"]],
            "hashes": [each["hash"] for each in injson["data"]],
            "originalfilenames": [each["originalfilename"] for each in injson["data"]]
           } 
    for det in range(len(injson["data"][0]["detector"])):
        for dp in range(len(injson["data"])):
            xs[det] = np.add(xs[det], [i[0]*weights[dp] for i in injson["data"][dp]["detector"][det]["signal"]])
            ys[det] = np.add(ys[det], [i[1]*weights[dp] for i in injson["data"][dp]["detector"][det]["signal"]])
        xs[det] = xs[det] / sum(divs)
        ys[det] = ys[det] / sum(divs)
        weighted = {
                    "samplerate": injson["data"][0]["detector"][det]["samplerate"],
                    "points": injson["data"][0]["detector"][det]["points"],
                    "units": injson["data"][0]["detector"][det]["units"],
                    "signal": list(zip(xs[det],ys[det]))
                   }
        data["detector"].append(weighted)
    return data
        
