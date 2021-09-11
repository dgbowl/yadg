import datetime
from ..helpers import *

def process(fn, **kwargs):
    with open(fn, "r", encoding="utf8",  errors='ignore') as infile:
        lines = infile.readlines()
    trace = {
        "version": lines.pop(0).split("Version:")[1].strip(),
        "maxchannels": int(lines.pop(0).split("Maxchannels:")[1].strip()),
        "sampleid": lines.pop(0).split("ID:")[1].strip(),
        "origfn": lines.pop(0).split("File:")[1].strip(),
        "method": lines.pop(0).split("Method:")[1].strip(),
        "user": lines.pop(0).split("Name:")[1].strip(),
        "uts": dateutils.coerceDateTime(lines.pop(0).split("Time:")[1].strip()),
        "trace": {}
    }
    samplerates = [each.strip() for each in lines.pop(0).split("Rate:")[1].split()]
    if samplerates[-1] == "Hz":
        samplerate = [float(sr) for sr in samplerates[:-1]]
    else:
        raise
    ndet = len(samplerate)
    points = [each.strip() for each in lines.pop(0).split(":")[1].split()]
    points = [int(points[i]) for i in range(len(samplerate))]
    xunits = [each.strip() for each in lines.pop(0).split(":")[1].split()]
    yunits = [each.strip() for each in lines.pop(0).replace("25 V","25µV").split(":")[1].split()]
    xmuls = [float(each) for each in lines.pop(0).split(":")[1].split()]
    ymuls = [float(each) for each in lines.pop(0).split(":")[1].split()]
    assert len(points) == len(xunits) == len(yunits) == len(xmuls) == len(ymuls) == ndet, \
        f'GCASC: Inconsistent number of detectors in {fn}.'
    for xmul in xmuls:
        assert xmul == xmuls[0], \
            f'GCASC: X axis multipliers inconsistent: {xmul} vs {xmuls[0]} in {fn}.'
    for point in points:
        assert point == points[0], \
            f'GCASC: X axis length inconsistent: {point} vs {point[0]} in {fn}.'
    for sr in samplerate:
        assert sr == samplerate[0], \
            f'GCASC: X axis sample rate inconsistent: {sr} vs {samplerate[0]} in {fn}.'
    for xu in xunits:
        assert xu == xunits[0], \
            f'GCASC: X axis units inconsistent: {xu} vs {xunits[0]} in {fn}.'
    dt = 60 if xunits[0] == "Minutes" else 1
    x = [i * xmuls[0] * dt / samplerate[0] for i in range(points[0])]
    for i in range(ndet):
        y = []
        for ii in range(points[i]):
            y.append(float(lines.pop(0).strip()) * ymuls[i])
        trace["trace"][f'det_{i+1}'] = {
                                       "units": {"t": "s", "y": yunits[i]},
                                       "t": x, "y": y
                                       }
    return [trace]

