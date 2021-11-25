import logging
import json
import os
from typing import Union

import yadg.dgutils
import yadg.core

version = "4.0.0"


def calib_3to4(oldcal: dict, caltype: str) -> dict:
    newcal = {}
    if caltype == "calfile":
        for k, v in oldcal["detectors"].items():
            pd = {
                "window": (v.get("window", 3) - 1) // 2,
                "polyorder": v.get("poly", 2),
                "prominence": v.get("prominence", 1.0),
                "threshold": v.get("threshold", 1.0),
            }
            sp = {}
            for kk, vv in v["species"].items():
                if kk == "units" and vv == "min":
                    continue
                spec = {
                    "l": vv["l"] * 60.0,
                    "r": vv["r"] * 60.0,
                    "calib": {"inverse": {"slope": vv.get("rf", 1.0)}},
                }
                sp[kk] = spec
            id = {"det_1": 0, "det_2": 1}[v["id"]]
            newcal[k] = {"id": id, "peakdetect": pd, "species": sp}
    elif caltype == "Tcalfile":
        newcal = {"T": {"T_f": {"calib": {"linear": oldcal}}, "unit": "C"}}
    elif caltype == "MFCcalfile":
        newcal = {}
        for k, v in oldcal.items():
            items = v.get("content", {k: 1.0})
            for kk, vv in items.items():
                if kk not in newcal:
                    newcal[kk] = {"unit": "ml/min"}
                newcal[kk][k] = {
                    "calib": {
                        "linear": {
                            "slope": v.get("slope", 1.0),
                            "intercept": v.get("intercept", 0.0),
                        }
                    },
                    "fraction": vv,
                }
    return newcal


def schema_3to4(oldschema: list) -> dict:
    newschema = {
        "metadata": {
            "provenance": {
                "yadg": yadg.dgutils.get_yadg_metadata(),
                "update_schema": {"updater": "schema_3to4"},
            },
            "schema_version": version,
            "timezone": "localtime",
        },
        "steps": [],
    }
    for oldstep in oldschema:
        newstep = {}

        newstep["parser"] = oldstep["datagram"]
        if newstep["parser"] == "gctrace":
            newstep["parser"] = "chromtrace"

        if "paths" in oldstep["import"]:
            oldstep["import"]["files"] = oldstep["import"].pop("paths")
        newstep["import"] = oldstep["import"]

        if oldstep.get("export", None) is not None:
            newstep["tag"] = oldstep["export"]

        calib = {}
        species = {}
        detectors = {}
        parameters = {}
        for k, v in oldstep["parameters"].items():
            if k in ["Tcalfile", "MFCcalfile", "calfile"]:
                try:
                    with open(v, "r") as cf:
                        temp = calib_3to4(json.load(cf), k)
                    logging.info(
                        f"schema_3to4: Found calfile '{k}' at '{v}', "
                        f"will attempt to modernise the calibration."
                    )
                    if k == "calfile":
                        for kk, vv in temp.items():
                            species[kk] = vv.pop("species")
                            detectors[kk] = vv
                    else:
                        calib.update(temp)
                except IOError:
                    logging.warning(
                        f"schema_3to4: Error reading '{k}' file: '{v}'. "
                        f"Keeping original key-value pair."
                    )
                    parameters[k] = v
            elif k == "method" and v == "q0refl":
                v = "kajfez"
                parameters[k] = v
            else:
                parameters[k] = v
        if newstep["parser"] == "meascsv" and "flow" not in calib:
            calib["flow"] = {"flow high": {}, "flow low": {}, "unit": "ml/min"}
        if calib != {}:
            parameters["convert"] = calib
        if species != {}:
            parameters["species"] = species
        if detectors != {}:
            parameters["detectors"] = detectors
        if parameters != {}:
            newstep["parameters"] = parameters
        newschema["steps"].append(newstep)

    return newschema


def datagram_3to4(olddg: list) -> dict:
    logging.warning(
        "datagram_3to4: updating from datagram version 3.1.0 is lossy. It is "
        "considerably safer to update schema instead, and re-process the raw data."
    )

    newdg = {
        "metadata": {
            "provenance": {
                "yadg": yadg.dgutils.get_yadg_metadata(),
                "update_object": {"updater": "datagram_3to4", "version": version},
            },
            "datagram_version": version,
            "date": yadg.dgutils.now(asstr=True),
            "input_schema": {},
        },
        "steps": [],
    }

    oldschema = []
    for oldstep in olddg:
        step = {}
        oldschema.append(oldstep["input"])
        step["metadata"] = {
            "tag": oldstep["input"]["export"],
            "parser": oldstep["metadata"],
        }
        step["metadata"]["parser"]["update_object"] = {
            "version": version,
            "updater": "datagram_3to4",
        }

        step["data"] = []
        for timestep in oldstep["results"]:
            ts = {"raw": {}, "derived": {}}
            ts["uts"] = float(timestep.pop("uts"))

            if oldstep["input"]["datagram"] == "meascsv":
                if "files" in oldstep["input"]["import"]:
                    ts["fn"] = oldstep["input"]["import"]["files"][0]
                else:
                    ts["fn"] = oldstep["input"]["import"]["paths"][0]
            elif oldstep["input"]["datagram"] == "qftrace":
                ts["fn"] = timestep.pop("path")
            elif oldstep["input"]["datagram"] == "gctrace":
                ts["fn"] = timestep.pop("fn")

            for k, v in timestep.items():
                if oldstep["input"]["datagram"] == "meascsv":
                    if k == "raw":
                        for kk, vv in v.items():
                            if isinstance(vv, (int, str)):
                                ts["raw"][kk] = vv
                            else:
                                if kk.startswith("T"):
                                    s = 0.1
                                    u = "%" if kk.endswith("o") else "C"
                                elif kk == "pressure":
                                    s = 0.1
                                    u = "mBar"
                                elif kk == "heater flow":
                                    s = 0.1
                                    u = "l/min"
                                else:
                                    s = 0.1
                                    u = "ml/min"
                                ts["raw"][kk] = {"n": vv, "s": s, "u": u}
                    elif k == "T":
                        ts["derived"]["T"] = {"n": v, "s": 5.0, "u": "C"}
                    elif k == "flow":
                        ts["derived"]["flow"] = {"n": v, "s": 0.001, "u": "ml/min"}
                    elif k == "x":
                        ts["derived"]["xin"] = {}
                        for kk, vv in v.items():
                            ts["derived"]["xin"][kk] = {"n": vv, "s": 0.001, "u": "-"}

                elif oldstep["input"]["datagram"] == "qftrace":
                    if k in ["Q0", "f0"]:
                        ts["derived"][k[0]] = {
                            "n": v,
                            "s": [20.0 if k == "Q0" else 1000.0] * len(v),
                            "u": "-" if k == "Q0" else "Hz",
                        }

                elif oldstep["input"]["datagram"] == "gctrace":
                    if "peaks" not in ts["derived"]:
                        ts["derived"]["peaks"] = {}
                    if "xout" not in ts["derived"]:
                        ts["derived"]["xout"] = {}
                    if k in ["TCD", "FID"]:
                        ts["derived"]["peaks"][k] = {}
                        for kk, vv in v.items():
                            ts["derived"]["peaks"][k][kk] = {
                                "A": {"n": vv["A"], "s": 0.01 * vv["A"], "u": "-"},
                                "h": {"n": vv["h"], "s": 1.0, "u": "-"},
                                "c": {"n": vv["x"], "s": 0.01 * vv["x"], "u": "-"},
                            }
                            if kk not in ts["derived"]["xout"] or k == "FID":
                                ts["derived"]["xout"][kk] = {
                                    "n": vv["x"] / 100,
                                    "s": 0.01 * vv["x"] / 100,
                                    "u": "-",
                                }
            if oldstep["input"]["datagram"] == "gctrace":
                totx = sum([v["n"] for k, v in ts["derived"]["xout"].items()])
                for k in ts["derived"]["xout"].keys():
                    ts["derived"]["xout"][k]["n"] = ts["derived"]["xout"][k]["n"] / totx
                    ts["derived"]["xout"][k]["s"] = ts["derived"]["xout"][k]["s"] / totx
            step["data"].append(ts)
        newdg["steps"].append(step)
    newdg["metadata"]["input_schema"] = schema_3to4(oldschema)

    return newdg


def update_object(type: str, object: Union[list, dict]) -> dict:
    """
    Yadg's update worker function.

    This is the main function called when **yadg** is executed as ``yadg update``.
    The main idea is to allow a simple update pathway from older versions of `schema` and
    ``datagram`` files to the current latest and greatest.

    Currently supports:

     - updating ``schema`` version 3.1.0 to 4.0.0
     - updating ``datagram`` version 3.1.0 to 4.0.0, although you **really** should be
       updating the ``schema`` instead and re-processing files.

    Parameters
    ----------
    type
        The type of the passed object, either `"datagram"` or `"schema"`.

    object
        The object to be updated

    Returns
    -------
    newobj: dict
        The updated and validated `"datagram"` or `"schema"`.

    """
    assert type in [
        "datagram",
        "schema",
    ], f"update_object: Provided type '{type}' is not one of ['datagram', 'schema']. "

    oldver = None
    if isinstance(object, list):
        oldver = "3.1.0"

    assert oldver is not None, (
        f"update_object: Impossible to figure out old '{type}' version. "
        "Please convert manually."
    )

    # distribute to updaters
    if oldver.startswith("3.") and type == "schema":
        logging.info("update_object: Updating old schema.")
        newobj = schema_3to4(object)
    elif oldver.startswith("3.") and type == "datagram":
        logging.info("update_object: Updating old datagram.")
        newobj = datagram_3to4(object)
    elif oldver.startswith("4."):
        logging.info("update_object: Already at latest version, no update necessary.")
        newobj = object

    with open("temp.json", "w") as outfile:
        json.dump(newobj, outfile, indent=1)

    if type == "schema":
        logging.info("update_object: Validating new schema.")
        yadg.core.validators.validate_schema(
            newobj, strictfiles=False, strictfolders=False
        )
    elif type == "datagram":
        logging.info("update_object: Validating new datagram.")
        yadg.core.validators.validate_datagram(newobj)

    return newobj


def schema_from_preset(preset: dict, folder: str) -> dict:
    newmeta = {
        "provenance": {
            "yadg": yadg.dgutils.get_yadg_metadata(),
        },
        "schema_version": version,
    }
    preset["metadata"].update(newmeta)
    for step in preset["steps"]:
        k = "files" if "files" in step["import"] else "folders"
        newf = []
        for oldf in step["import"][k]:
            if os.path.isabs(oldf):
                logging.warning(
                    f"schema_from_preset: Item '{oldf}' in '{k}' is an absolute "
                    "path and will not be patched."
                )
            else:
                assert not oldf.startswith("." + os.path.sep), (
                    f"schema_from_preset: Item '{oldf}' in '{k}' does start "
                    f"with '.{os.path.sep}' and therefore should not be patched "
                    f"using '{folder}'."
                )
                newp = os.path.abspath(os.path.join(folder, oldf))
                newf.append(newp)
        step["import"][k] = newf
        if "calfile" in step["parameters"]:
            oldf = step["parameters"]["calfile"]
            if os.path.isabs(oldf):
                logging.warning(
                    f"schema_from_preset: Specified calfile '{oldf}' is an absolute "
                    "path and will not be patched."
                )
            else:
                newp = os.path.abspath(os.path.join(folder, oldf))
                step["parameters"]["calfile"] = newp
    return preset
