from packaging.version import Version
import logging
import os
from typing import Union
from dgbowl_schemas.yadg import to_dataschema
from dgbowl_schemas.yadg.dataschema import DataSchema
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModel_v1
from yadg import dgutils

__latest_dataschema__ = "5.1"
logger = logging.getLogger(__name__)


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
        newcal = {"T": {"T_f": {"calib": {"linear": oldcal}}, "unit": "degC"}}
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
                "type": "yadg update",
                "metadata": {
                    "yadg": dgutils.get_yadg_metadata(),
                    "update_schema": {"updater": "schema_3to4"},
                },
            },
            "version": "4.1",
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
        newstep["input"] = oldstep["import"]

        if oldstep.get("export", None) is not None:
            newstep["tag"] = oldstep["export"]

        parameters = {}
        for k, v in oldstep["parameters"].items():
            if k in ["Tcalfile", "MFCcalfile", "calfile"]:
                logger.warning(
                    "Parsing of post-processing parameter '%s' has been removed in "
                    "yadg-5.0, please use dgpost-2.0 to reproduce this functionality.",
                    k,
                )
            elif k == "method" and v == "q0refl":
                logger.warning(
                    "Parsing of post-processing parameter '%s' has been removed in "
                    "yadg-5.0, please use dgpost-2.0 to reproduce this functionality.",
                    k,
                )
            else:
                parameters[k] = v
        if parameters != {}:
            newstep["parameters"] = parameters
        newschema["steps"].append(newstep)

    return newschema


def update_schema(object: Union[list, dict, BaseModel, BaseModel_v1]) -> DataSchema:
    """
    The ``yadg update`` worker function.

    The main purpose is to allow a simple update pathway from older versions of
    dataschema files to the current latest and greatest.

    Currently supports:

     - updating dataschema version 3.1 to 4.0 using routines in ``yadg``,
     - updating dataschema version 4.0 and above to the latest dataschema using the
       in-built ``.update()`` mechanism.

    Parameters
    ----------
    object
        The object to be updated

    Returns
    -------
    newobj: dict
        The updated and validated `"datagram"` or `"schema"`.

    """

    if isinstance(object, list):
        logger.info("Updating list-style DataSchema")
        newobj = to_dataschema(**schema_3to4(object))
    elif isinstance(object, dict):
        logger.info("Updating dict-style DataSchema")
        newobj = to_dataschema(**object)
    elif isinstance(object, (BaseModel, BaseModel_v1)):
        logger.info("Updating an existing DataSchema object")
        newobj = object
    else:
        raise ValueError(f"Supplied object is of incorrect type: {type(object)}")

    maxver = Version(__latest_dataschema__)
    while hasattr(newobj, "update"):
        temp = newobj.update()
        if hasattr(temp, "version"):
            if Version(temp.version) > maxver:
                break
        newobj = temp
    return newobj


def schema_from_preset(preset: DataSchema, folder: str) -> DataSchema:
    # preset.metadata["provenance"] = "yadg preset"
    for step in preset.steps:
        for fi, fn in enumerate(step.input.files):
            if os.path.isabs(fn):
                logger.warning(
                    "Item '%s' in '%s' is an absolute path and will not be patched.",
                    fn,
                    step,
                )
            else:
                step.input.files[fi] = os.path.abspath(os.path.join(folder, fn))
        if (
            step.externaldate is not None
            and hasattr(step.externaldate.using, "file")
            and step.externaldate.using.file is not None
        ):
            oldf = step.externaldate.using.file.path
            if os.path.isabs(oldf):
                logger.warning(
                    "Specified externaldate file '%s' is an absolute path "
                    "and will not be patched.",
                    oldf,
                )
            else:
                newf = os.path.abspath(os.path.join(folder, oldf))
                step.externaldate.using.file.path = newf
    return preset
