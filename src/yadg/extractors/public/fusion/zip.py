from datatree import DataTree
from yadg.parsers.chromdata.fusionzip import process as extract_data
from yadg.parsers.chromtrace.fusionzip import process as extract_trace


supports = {
    "fusion.zip",
}


def extract(**kwargs):
    data = extract_data(**kwargs)
    trace = extract_trace(**kwargs)
    newdt = DataTree(data)
    for k, v in trace.items():
        newdt[k] = v
    return newdt


__all__ = ["supports", "extract"]
