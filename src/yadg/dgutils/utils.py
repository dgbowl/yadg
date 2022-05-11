import logging
import json
import os
from typing import Union
from packaging import version
from dgbowl_schemas.yadg import to_dataschema, latest_version

from .. import dgutils
from .. import core

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
            "version": latest_version,
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

        calib = {}
        species = {}
        detectors = {}
        parameters = {}
        for k, v in oldstep["parameters"].items():
            if k in ["Tcalfile", "MFCcalfile", "calfile"]:
                try:
                    with open(v, "r") as cf:
                        temp = calib_3to4(json.load(cf), k)
                    logger.info(
                        "Found calfile '%s' at '%s', "
                        "will attempt to modernise the calibration.",
                        k,
                        v,
                    )
                    if k == "calfile":
                        for kk, vv in temp.items():
                            species[kk] = vv.pop("species")
                            detectors[kk] = vv
                    else:
                        calib.update(temp)
                except IOError:
                    logger.error(
                        "Error reading '%s' file: '{k}'. "
                        "Keeping original key-value pair.",
                        k,
                        v,
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


def update_object(objtype: str, object: Union[list, dict]) -> dict:
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
    objtype
        The type of the passed object, either `"datagram"` or `"schema"`.

    object
        The object to be updated

    Returns
    -------
    newobj: dict
        The updated and validated `"datagram"` or `"schema"`.

    """
    assert objtype in {"datagram", "schema"}, (
        f"Type '{objtype}' provided to update_object "
        "is not one of {'datagram', 'schema'}."
    )

    oldver = None
    if isinstance(object, list):
        oldver = "3.1.0"

    assert oldver is not None, (
        f"update_object: Impossible to figure out old '{type}' version. "
        "Please convert manually."
    )

    # distribute to updaters
    if version.parse(oldver).major == 3:
        assert (
            objtype == "schema"
        ), "Updating datagrams older than version 4.0.0 is not possible"
        logger.info("Updating old schema %s -> %s", oldver, latest_version)
        newobj = schema_3to4(object)
    elif version.parse(oldver).major == 4:
        logger.info("Already at latest version, no update necessary.")
        newobj = object

    with open("temp.json", "w") as outfile:
        json.dump(newobj, outfile, indent=1)

    if objtype == "schema":
        logger.info("Validating new schema.")
        newobj = to_dataschema(**newobj)
    elif objtype == "datagram":
        logger.info("Validating new datagram.")
        core.validators.validate_datagram(newobj)

    return newobj


def schema_from_preset(preset: dict, folder: str) -> dict:
    if isinstance(preset["metadata"]["provenance"], str):
        preset["metadata"]["provenance"] = "yadg preset"
    elif isinstance(preset["metadata"]["provenance"], dict):
        preset["metadata"]["provenance"] = {
            "type": "yadg preset",
            "metadata": {"preset_provenance": preset["metadata"]["provenance"]},
        }
    for step in preset["steps"]:
        inpk = "import" if "import" in step else "input"
        filk = "files" if "files" in step[inpk] else "folders"
        newf = []
        for oldf in step[inpk][filk]:
            if os.path.isabs(oldf):
                logger.warning(
                    "Item '%s' in '%s' is an absolute path and will not be patched.",
                    oldf,
                    filk,
                )
            else:
                assert not oldf.startswith("." + os.path.sep), (
                    f"Item '{oldf}' in '{filk}' does start with '.{os.path.sep}' and "
                    f"therefore should not be patched using '{folder}'."
                )
                newp = os.path.abspath(os.path.join(folder, oldf))
                newf.append(newp)
        step[inpk][filk] = newf
        if "calfile" in step["parameters"]:
            oldf = step["parameters"]["calfile"]
            if os.path.isabs(oldf):
                logger.warning(
                    "Specified calfile '%s' is an absolute path "
                    "and will not be patched.",
                    oldf,
                )
            else:
                newp = os.path.abspath(os.path.join(folder, oldf))
                step["parameters"]["calfile"] = newp
        if "externaldate" in step:
            using = "from" if "from" in step["externaldate"] else "using"
            if "file" in step["externaldate"][using]:
                oldf = step["externaldate"][using]["file"]["path"]
                if os.path.isabs(oldf):
                    logger.warning(
                        "Specified externaldate file '%s' is an absolute path "
                        "and will not be patched.",
                        oldf,
                    )
                else:
                    newp = os.path.abspath(os.path.join(folder, oldf))
                    step["externaldate"][using]["file"]["path"] = newp
    return preset
