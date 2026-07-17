from packaging.version import Version
import logging
import os
from dgbowl_schemas.yadg import to_dataschema
from dgbowl_schemas.yadg.dataschema import DataSchema
from pydantic import BaseModel

__latest_dataschema__ = "7.0"
logger = logging.getLogger(__name__)


def update_schema(obj: list | dict | BaseModel) -> DataSchema:
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

    if isinstance(obj, list):
        logger.info("Coercing list-style DataSchema to dict")
        obj = {"version": "3.1", "steps": obj}

    if isinstance(obj, dict):
        logger.info("Updating dict-style DataSchema")
        newobj = to_dataschema(**obj)
    elif isinstance(object, BaseModel):
        logger.info("Updating an existing DataSchema object")
        newobj = obj
    else:
        raise ValueError(f"Supplied object is of incorrect type: {type(obj)}")

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
