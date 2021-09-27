import numpy as np

def _list_validator(l):
    if len(l) == 3:
        return _float_list(l)
    else:
        return _general_list(l)

def _float_list(l):
    if (isinstance(l[0], (float, np.inexact, complex)) and \
        isinstance(l[1], (float, np.inexact, complex)) and isinstance(l[2], str)): 
        return True
    else:
        return _general_list(l)

def _general_list(l):
    for v in l:
        if isinstance(v, list):
            assert _list_validator(v)
        elif isinstance(v, dict):
            assert _dict_validator(v)
        else:
            assert isinstance(v, str) or isinstance(v, (int, np.integer)), \
                "List elements have to be one of [str, int, dict, list], " \
                f"but entry id:{l.index(v)}:{type(v)} is neither: {l}"
    return True

def _dict_validator(d):
    for k, v in d.items():
        if isinstance(v, (float, np.inexact)):
            assert k == "uts", \
                f"Only 'uts':float can be a float entry, not '{k}'."
        elif isinstance(v, list):
            assert _list_validator(v)
        elif isinstance(v, dict):
            assert _dict_validator(v)
        else:
            assert isinstance(v, str) or isinstance(v, (int, np.integer)), \
                "Dict elements have to be one of [str, int, dict, list], " \
                f"but '{k}':{type(v)} is neither: {v}"
    return True

def object_is_datagram(dg):
    # top level tests
    assert isinstance(dg, dict), \
        "Datagram must be a dict."
    assert len(set(["metadata", "data"]) & set(dg.keys())) == 2 and \
        isinstance(dg["metadata"], dict) and isinstance(dg["data"], list), \
        "Datagram must have 'metadata':dict and 'data':list entries."
    # metadata contents
    assert len(set(["yadg", "date"]) & set(dg["metadata"].keys())) == 2 and \
        isinstance(dg["metadata"]["yadg"], dict) and isinstance(dg["metadata"]["date"], str), \
        "Top-level 'metadata' entry must contain the entries 'yadg':dict and 'date':str."
    # data contents
    for step in dg["data"]:
        keys = step.keys()
        assert len(set(["metadata", "timesteps"]) & set(keys)) == 2 and \
            isinstance(step["metadata"], dict) and isinstance(step["timesteps"], list) and \
            (("common" in keys and len(keys) == 3 and isinstance(step["common"], dict)) or (len(keys) == 2)), \
            "Each step has to have a 'metadata':dict and 'timesteps':list entries," \
            "additionally a 'common':dict entry is allowed."
        assert ("fn" in step["metadata"] and isinstance(step["metadata"]["fn"], str)) ^ \
            (all(["fn" in ts for ts in step["timesteps"]]) and \
             all([isinstance(ts["fn"], str) for ts in step["timesteps"]])), \
            "The 'fn':str entry has to be provided either in the 'metadata' entry " \
            "of each step, or in each element of 'timesteps."
        # metadata contents
        assert "input" in step["metadata"] and isinstance(step["metadata"]["input"], dict), \
            "An 'input':dict entry containing the schema has to be in 'metadata'."
        assert "tag" in step["metadata"] and isinstance(step["metadata"]["tag"], str), \
            "An 'tag':str entry has to be in 'metadata'."
        # timestep contents
        for ts in step["timesteps"]:
            assert isinstance(ts, dict), \
                "Timesteps have to be dict."
            assert "uts" in ts.keys() and isinstance(ts["uts"], float), \
                "A 'uts':float timestamp entry has to be in each timestep."
            assert _dict_validator(ts)