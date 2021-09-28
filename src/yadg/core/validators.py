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

    -  The `datagram` must be a (dict) with two entries:

       - ``"metadata"`` (dict): A top-level entry containing metadata. 
       - ``"data"`` (list): List corresponding to a sequence of `step`\ s.

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

def validate_schema(schema: Union[list, tuple], strictfiles: bool = False) -> True:
    """
    Schema validator. 
    
    Checks the overall `schema` format, checks every `step` of the `schema` for 
    required entries, and checks whether required parameters for each `parser` 
    are provided. The validator additionally fills in optional parameters, where
    necessary for a valid `schema`.

    The specification is:
    
    - The `schema` has to be (Union[list, tuple])
    - Each element of this parent list is a `step` (dict)
    - Each `step` has to have the ``"parser"`` and ``"import"`` entries:
    
      - The ``"parser"`` (str) entry has contain the name of the requested 
        parser module. This entry is processed in the :meth:`_infer_datagram_handler`
        function in this module.
      - The ``"import"`` (dict) entry has to contain:
      
        - Exactly **one** entry out of ``"files"``, ``"folders"``, or ``"paths"``.
          This entry must be a (list) even if only one element is provided. 
        - Any combination of ``"prefix"``, ``"suffix"``, ``"contains"`` entries,
          which must be a (str). These entries specify the matching of files 
          within folders accordingly.
        
    - The only other allowed entries are:
    
      - ``"tag"`` (str): for defining a tag for each `step`; by default assigned
        the numerical index of the `step` within the `schema`.
      - ``"export"`` (str): for `step` export; if the processed `step` should be
        exported as a ``json`` file which is kept available for other `step`\ s
      - ``"parameters"`` (dict): for specifying other parameters for the parser.
      
    - no other entries are permitted

    Parameters
    ----------
    schema
        The schema to be validated.
    
    strictfiles
        When `True`, any files specified using the ``"files"`` option will not 
        be checked for existence. Note that folders (specified via ``"folders"``) 
        are always checked.
    
    Returns
    -------
    True: bool
        When the `schema` is valid and passes all assertions, `True` is returned.
    """
    # schema has to be a list or a tuple
    assert isinstance(schema, (list, tuple)), \
        logging.error("schema_validator: Provided schema is neither list nor a tuple.")
    requiredkeys = {
        "parser": {
            "one": ["dummy", "basiccsv", "qftrace", "gctrace"],
            "any": []
        }, 
        "import": {
            "one": ["files", "folders", "paths"], 
            "any": ["prefix", "suffix", "contains"]
        }
    }
    for step in schema:
        si = schema.index(step)
        allowedkeys = {
            "tag": f"{si:03d}", 
            "export": None, 
            "parameters": {}
        }
        # step in a schema has to be a dict
        assert isinstance(step, dict), \
            logging.error(f"schema_validator: Step {si} of schema is not a dict.")
        # all required keys have to be in a step
        assert len(set(requiredkeys.keys()) & set(step.keys())) == len(requiredkeys.keys()), \
            logging.error(f"schema_validator: Step {si} does not contain all "
                          f"required keys: {list(requiredkeys.keys())}")
        for kreq, vreq in requiredkeys.items():
            # exactly one of entries in "one" must be present
            assert (isinstance(step[kreq], str) and step[kreq] in vreq["one"]) or \
                   (isinstance(step[kreq], dict) and len(set(step[kreq]) & set(vreq["one"])) == 1), \
                logging.error(f"schema_validator: More than one of exclusive "
                              f"'{kreq}' entries from {vreq['one']} was provided.")
            # additionally, only entries in "any" are present
            if isinstance(step[kreq], dict):
                for key in step[kreq]:
                    if key in vreq["one"]:
                        continue
                    assert key in vreq["any"], \
                        logging.error(f"schema_validator: Undefined entry {key} was"
                                      f"supplied as a parameter for a required key {kreq}.")
        # validate "import" spec
        if "paths" in step["import"]:
            step["import"]["files"] = step["import"].pop("paths")
        if "files" in step["import"] and not strictfiles:
            for path in step["import"]["files"]:
                assert os.path.exists(path) and os.path.isfile(path), \
                    logging.error(f"schema_validator: File {path} specified in "
                                  f"'import' of step {si} is not a file.")
        if "folders" in step["import"]:
            for path in step["import"]["folders"]:
                assert os.path.exists(path) and os.path.isdir(path), \
                    logging.error(f"schema_validator: Folder {path} specified in "
                                  f"'import' of step {si} is not a folder.")
        # additionally, only entries in allowedkeys are permitted; fill defaults
        for key, kdef in allowedkeys.items():
            if key in step:
                assert isinstance(step[key], type(kdef)) or step[key] is None, \
                    logging.error(f"schema_validator: Step {si} contains {key} of "
                                  f"the wrong type {type(step[key])}.")
            if key not in step or step[key] is None:
                step[key] = kdef
        # validate supplied parameters
        for key, val in step["parameters"].items():
            # validation of "timestamp" spec
            if key == "timestamp":
                assert isinstance(val, dict), \
                    logging.error(f"schema_validator: Value of {key} in 'parameters'"
                                  f" of step {si} is not a dict.")
                allowedtimestamps = ["uts", "timestamp", "date", "time"]
                for k, v in val.items():
                    assert k in allowedtimestamps, \
                        logging.error("schema_validator: timestamp has to be one of "
                                      f"{allowedtimestamps}, not {k}.")
                    assert (isinstance(v, (tuple, list)) and len(v) == 2) or isinstance(v, int), \
                        logging.error("schema_validator: timestamp specification has"
                                      "to be column index (int), or a tuple/list "
                                      "with a column index (int) and format (string).")
    return True