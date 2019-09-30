import json
import numpy as np
from dbutils import *

_VERSION = 0.1

def combine(filelist, **kwargs):
    datagramlist = []
    for fn in filelist:
        with open(fn, "r") as infile:
            fndata = json.load(infile)
        for datagram in fndata:
            datagramlist.append(datagram)
    return(datagramlist)

def reduce(datagramfile, **kwargs):
    tasktype = kwargs.pop("parameters", {"type": "avg"})["type"]
    assert tasktype in ["avg", "sum", "diff"] , \
        f'DGUTILS: reduce provided with an incorrent "type": {tasktype}.'
    with open(datagramfile, "r") as infile:
        origdg = json.load(infile)
    if tasktype == "avg":
        weights = [len(origdg) for i in range(len(origdg))]
    elif tasktype == "sum":
        weights = [1 for i in range(len(origdg))]
    elif tasktype == "diff":
        weights = [1] + [-1 for i in range(len(origdg)-1)]
    dgzero = np.array(origdg[0]["datastream"])
    print(dgzero.shape)
    flatresult = [0.0 for i in dgzero.flatten()]
    for datagram in origdg:
        dgi = np.array(datagram["datastream"])
        assert dgi.shape == dgzero.shape, \
            f'DGUTILS: reduce provided with inconsistent datagram shapes.'
        weight = float(weights.pop(0))
        for i in range(len(flatresult)):
            flatresult[i] += dgi.flatten()[i] / weight
    result = {}
    result["datastream"] = np.array(flatresult).reshape(dgzero.shape).tolist()
    result["metadata"] = {}
    result["metadata"]["units"] = origdg[0]["metadata"]["units"]
    result["metadata"]["version"] = kwargs.get("ver", {})
    result["metadata"]["version"]["reduce"] = _VERSION
    return(result)
    
def printdg(datagram, **kwargs):
    print(len(datagram))
    
