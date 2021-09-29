import numpy as np
import logging
import os
from typing import Union

def _list_validator(l: list) -> bool:
    if len(l) == 3:
        return _float_list(l)
    else:
        return _general_list(l)

def _float_list(l: list) -> bool:
    if (isinstance(l[0], (float, np.inexact, complex)) and \
        isinstance(l[1], (float, np.inexact, complex)) and isinstance(l[2], str)): 
        return True
    else:
        return _general_list(l)

def _general_list(l: list) -> bool:
    for v in l:
        if isinstance(v, list):
            return _list_validator(v)
        elif isinstance(v, dict):
            return _dict_validator(v)
        else:
            assert isinstance(v, str) or isinstance(v, (int, np.integer)), \
                "List elements have to be one of [str, int, dict, list], " \
                f"but entry id:{l.index(v)}:{type(v)} is neither: {l}"
    return True

def _dict_validator(d: dict) -> bool:
    for k, v in d.items():
        if isinstance(v, (float, np.inexact)):
            assert k == "uts", \
                f"Only 'uts':float can be a float entry, not '{k}'."
        elif isinstance(v, list):
            return _list_validator(v)
        elif isinstance(v, dict):
            return _dict_validator(v)
        else:
            assert isinstance(v, str) or isinstance(v, (int, np.integer)), \
                "Dict elements have to be one of [str, int, dict, list], " \
                f"but '{k}':{type(v)} is neither: {v}"
    return True

def validate_datagram(datagram: dict) -> True:
    """
    Datagram validator.

    Checks the overall `datagram` format using a series of assertions.

    The current `datagram` specification is:

    -  The `datagram` must be a :class:`(dict)` with two entries:

       - ``"metadata"`` :class:`(dict)`: A top-level entry containing metadata. 
       - ``"data"`` :class:`(list[dict])`: List corresponding to a sequence of `steps`.

    Parameters
    ----------
    datagram
        The `datagram` to be validated.
    
    Returns
    -------
    True: bool
        If the `datagram` passes all assertions, returns `True`. Else,
        an AssertionError is raised.

    """
    # top level tests
    assert isinstance(datagram, dict), \
        "Datagram must be a dict."
    assert len({"metadata", "data"}.intersection(datagram.keys())) == 2 and \
        isinstance(datagram["metadata"], dict) and isinstance(datagram["data"], list), \
        "Datagram must have 'metadata':dict and 'data':list entries."
    # metadata contents
    assert len({"yadg", "date"}.intersection(datagram["metadata"].keys())) == 2 and \
        isinstance(datagram["metadata"]["yadg"], dict) and isinstance(datagram["metadata"]["date"], str), \
        "Top-level 'metadata' entry must contain the entries 'yadg':dict and 'date':str."
    # data contents
    for step in datagram["data"]:
        keys = step.keys()
        assert len({"metadata", "timesteps"}.intersection(keys)) == 2 and \
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
    return True


def _step_validator(item: Union[list, dict, str], spec: dict) -> True:
    assert isinstance(item, spec["type"]), f"validate_schema: item '{item}' does " \
                                           f"not match prescribed type in spec " \
                                           f"'{spec['type']}'."
    if len({"all", "one", "any"}.intersection(spec)) > 0 and spec["type"] in [list, dict]:
        for k, v in spec.get("all", {}).items():
            assert k in item, f"validate_schema: required entry '{k}' was not " \
                              f"specified in item '{item}'."
        if "one" in spec:
            initem = set(spec["one"]).intersection(item)
            assert len(initem) == 1, f"validate_schema: Exactly one of entries in " \
                                     f"{spec['one']} has to be provided in item {item}, " \
                                     f"but {len(initem)} were provided: {initem}"
        for k in item:
            s = False
            for d in ["all", "one", "any"]:
                if k in spec.get(d, []):
                    s = d
            assert s, f"validate_schema: Key '{k}' in item {item} is not understood."
            assert _step_validator(item[k], spec[s][k])
    elif len({"all", "one", "any"}.intersection(spec)) > 0 and spec["type"] in [str]:
        if "all" in spec:
            assert len(spec["all"]) == 1 and item in spec["all"], \
                    f"validate_schema: Item '{item}' is not in {spec['all']}."
        if "one" in spec:
            assert item in spec["one"], \
                    f"validate_schema: Item '{item}' is not in {spec['one']}."
        if "any" in spec:
            assert item in spec["any"], \
                    f"validate_schema: Item '{item}' is not in {spec['any']}."
    return True

def validate_schema(schema: Union[list, tuple], strictfiles: bool = True) -> True:
    """
    Schema validator. 
    
    Checks the overall `schema` format, checks every `step` of the `schema` for 
    required entries, and checks whether required parameters for each `parser` 
    are provided. The validator additionally fills in optional parameters, where
    necessary for a valid `schema`.

    The specification is:
    
    - The `schema` has to be a :class:`(Union[list, tuple])`
    - Each element of this parent list is a `step`, of type :class:`(dict)`
    - Each `step` has to have the ``"parser"`` and ``"import"`` entries:
    
      - The ``"parser"`` is a :class:`(str)` entry that has to contain the name 
        of the requested parser module. This entry is processed in the 
        :func:`yadg.core.main._infer_datagram_handler` function in the core module.
      - The ``"import"`` is a :class:`(dict)` entry has to contain:
      
        - Exactly **one** entry out of ``"files"`` or ``"folders"``.
          This entry must be a :class:`(list)` even if only one element is provided. 
        - Any combination of ``"prefix"``, ``"suffix"``, ``"contains"`` entries.
          They must be of type :class:`(str)`. These entries specify the matching 
          of files within folders accordingly.
        
    - The only other allowed entries are:
    
      - ``"tag"`` :class:`(str)`: for defining a tag for each `step`; by default 
        assigned the numerical index of the `step` within the `schema`.
      - ``"export"`` :class:`(str)`: for exporting a single `step`; whether the 
        processed `step` should be exported as a ``json`` file. This file is kept 
        available for other `steps`, but will be removed at the end of `schema`
        processing.
      - ``"parameters"`` :class:`(dict)`: for specifying other parameters for 
        each of the parsers.
      
    - no other entries are permitted

    Parameters
    ----------
    schema
        The schema to be validated.
    
    strictfiles
        When `False`, any files specified using the ``"files"`` option will not 
        be checked for existence. Note that folders (specified via ``"folders"``) 
        are always checked.
    
    Returns
    -------
    True: bool
        When the `schema` is valid and passes all assertions, `True` is returned.
    """
    spec = {
        "type": dict,
        "all": {
            "parser": {
                "type": str,
                "one": ["dummy", "basiccsv", "qftrace", "gctrace"]
            },
            "import": {
                "type": dict,
                "one": {
                    "files": {"type": list},
                    "folders": {"type": list}
                },
                "any": {
                    "prefix": {"type": str},
                    "suffix": {"type": str},
                    "contains": {"type": str}
                }
            }
        },
        "any": {
            "tag": {"type": str},
            "export": {"type": str},
            "parameters": {"type": dict}
        }
    }
    # schema has to be a list or a tuple
    assert isinstance(schema, (list, tuple)), "schema_validator: Provided schema " \
                                              "is neither a list nor a tuple."
    
    for step in schema:
        si = schema.index(step)
        # schema has to meet spec defined above
        assert _step_validator(step, spec)
        # import files or folders must exist
        if "files" in step["import"] and strictfiles:
            for fn in step["import"]["files"]:
                assert os.path.exists(fn) and os.path.isfile(fn), \
                        f"schema_validator: File path {fn} provided in " \
                        f"step {si} is not a valid file."
        if "folders" in step["import"]:
            for fn in step["import"]["folders"]:
                assert os.path.exists(fn) and os.path.isdir(fn), \
                        f"schema_validator: Folder path {fn} provided in " \
                        f"step {si} is not a valid folder."
        # supply a default tag
        if "tag" not in step:
            logging.info(f"schema_validator: Tag not present in step {si}.")
            step["tag"] = f"{si:2d}"
    return True
        

    #     # step in a schema has to be a dict
    #     assert isinstance(step, dict), \
    #         logging.error(f"schema_validator: Step {si} of schema is not a dict.")
    #     for k, v in spec["all"].items():
    #         # all from 'all' keys must be in each schema
    #         assert k in step and isinstance(step[k], v["type"])
    #     "tag": f"{si:03d}", 
    #         "export": None, 
    #         "parameters": {}
    #     }
    #     # all required keys have to be in a step
    #     assert len(set(requiredkeys.keys()) & set(step.keys())) == len(requiredkeys.keys()), \
    #         logging.error(f"schema_validator: Step {si} does not contain all "
    #                       f"required keys: {list(requiredkeys.keys())}")
    #     for kreq, vreq in requiredkeys.items():
    #         # exactly one of entries in "one" must be present
    #         assert (isinstance(step[kreq], str) and step[kreq] in vreq["one"]) or \
    #                (isinstance(step[kreq], dict) and len(set(step[kreq]) & set(vreq["one"])) == 1), \
    #             logging.error(f"schema_validator: More than one of exclusive "
    #                           f"'{kreq}' entries from {vreq['one']} was provided.")
    #         # additionally, only entries in "any" are present
    #         if isinstance(step[kreq], dict):
    #             for key in step[kreq]:
    #                 if key in vreq["one"]:
    #                     continue
    #                 assert key in vreq["any"], \
    #                     logging.error(f"schema_validator: Undefined entry {key} was"
    #                                   f"supplied as a parameter for a required key {kreq}.")
    #     # validate "import" spec
    #     if "paths" in step["import"]:
    #         step["import"]["files"] = step["import"].pop("paths")
    #     if "files" in step["import"] and not strictfiles:
    #         for path in step["import"]["files"]:
    #             assert os.path.exists(path) and os.path.isfile(path), \
    #                 logging.error(f"schema_validator: File {path} specified in "
    #                               f"'import' of step {si} is not a file.")
    #     if "folders" in step["import"]:
    #         for path in step["import"]["folders"]:
    #             assert os.path.exists(path) and os.path.isdir(path), \
    #                 logging.error(f"schema_validator: Folder {path} specified in "
    #                               f"'import' of step {si} is not a folder.")
    #     # additionally, only entries in allowedkeys are permitted; fill defaults
    #     for key, kdef in allowedkeys.items():
    #         if key in step:
    #             assert isinstance(step[key], type(kdef)) or step[key] is None, \
    #                 logging.error(f"schema_validator: Step {si} contains {key} of "
    #                               f"the wrong type {type(step[key])}.")
    #         if key not in step or step[key] is None:
    #             step[key] = kdef
    #     # validate supplied parameters
    #     for key, val in step["parameters"].items():
    #         # validation of "timestamp" spec
    #         if key == "timestamp":
    #             assert isinstance(val, dict), \
    #                 logging.error(f"schema_validator: Value of {key} in 'parameters'"
    #                               f" of step {si} is not a dict.")
    #             allowedtimestamps = ["uts", "timestamp", "date", "time"]
    #             for k, v in val.items():
    #                 assert k in allowedtimestamps, \
    #                     logging.error("schema_validator: timestamp has to be one of "
    #                                   f"{allowedtimestamps}, not {k}.")
    #                 assert (isinstance(v, (tuple, list)) and len(v) == 2) or isinstance(v, int), \
    #                     logging.error("schema_validator: timestamp specification has"
    #                                   "to be column index (int), or a tuple/list "
    #                                   "with a column index (int) and format (string).")
    # return True