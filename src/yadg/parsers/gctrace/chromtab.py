import datetime
#from helpers import *

def process(fn, **kwargs):
    with open(fn, "r", encoding="utf8", errors="ignore") as infile:
        lines = infile.readlines()
    tis = []
    for li in range(len(lines)):
        if "Path" in lines[li]:
            tis.append(li)
    traces = []
    print(tis)
    for ti in tis:
        path, origfn, datetime, sample, misc = [each.strip('"').strip() for each in lines[ti+1].split(",")]
        trace = {
            "sampleid": sample,
            "origfn": origfn,
            "method": "n/a",
            "uts": dateutils.coerceStringDate(datetime),
            "trace": {}
        }
        i = 0
        li = 2
        x = []
        y = []
        while ti + li < len(lines) - 1:
            li += 1
            if lines[ti+li].startswith('"'):
                if "Path" in lines[ti+li]:
                    break
                else:
                    trace["trace"][f"det_{i+1}"] = {"units": {"t": "s", "y": "--"}, "t": x, "y": y}
                    i += 1
                    x = []
                    y = []
                    continue
            xy = lines[ti+li].split(",")
            x.append(float(xy[0])*60)
            y.append(float(xy[1]))
        trace["trace"][f"det_{i+1}"] = {"units": {"t": "s", "y": "--"}, "t": x, "y": y}
        traces.append(trace)
    return traces

