"""
**fusionjson**: Processing Inficon Fusion json data format (json).
------------------------------------------------------------------

This is a fairly detailed data format, including the traces, the calibration applied,
and also the integrated peak areas and other processed information, which are parsed
by this module.

.. note ::

    To parse the raw trace data, use the :mod:`~yadg.parsers.chromtrace` module.

.. warning ::

    The detectors in the json files are not necessarily in a consistent order. To
    avoid inconsistent parsing of species which appear in both detectors, the
    detector keys are sorted. **Species present in both detectors** will be
    **overwritten by the last detector** in alphabetical order.

Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      username: None
      version:  !!str
      datafile: !!str

.. codeauthor:: Peter Kraus
"""
import json
import logging
from zoneinfo import ZoneInfo
from ...dgutils.dateutils import str_to_uts
import xarray as xr
import numpy as np

logger = logging.getLogger(__name__)


def process(
    *, fn: str, encoding: str, timezone: ZoneInfo, **kwargs: dict
) -> xr.Dataset:
    """
    Fusion json format.

    One chromatogram per file with multiple traces, and pre-analysed results.
    Only a subset of the metadata is retained, including the method name,
    detector names, and information about assigned peaks.

    Parameters
    ----------
    fn
        Filename to process.

    encoding
        Encoding used to open the file.

    timezone
        Timezone information. This should be ``"localtime"``.

    Returns
    -------
    :class:`xarray.Dataset`

    """

    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        jsdata = json.load(infile)
    metadata = {
        "method": jsdata.get("methodName", "n/a"),
        "version": jsdata.get("softwareVersion", {}).get("version", None),
        "datafile": jsdata.get("sequence", {}).get("location", None),
    }
    uts = str_to_uts(timestamp=jsdata["runTimeStamp"], timezone=timezone)

    sampleid = jsdata.get("annotations", {}).get("name", None)
    if sampleid is not None:
        metadata["sampleid"] = sampleid

    units = {
        "height": None,
        "area": None,
        "concentration": "%",
        "xout": "%",
        "retention time": "s",
    }

    raw = {
        "height": {},
        "area": {},
        "concentration": {},
        "xout": {},
        "retention time": {},
    }

    species = set()

    # sort detector keys to ensure alphabetic order for ID matching
    for detname in sorted(jsdata["detectors"].keys()):
        detdict = jsdata["detectors"][detname]
        if "analysis" in detdict:
            for peak in detdict["analysis"]["peaks"]:
                if "label" not in peak:
                    continue
                else:
                    species.add(peak["label"])
                if "height" in peak:
                    raw["height"][peak["label"]] = (float(peak["height"]), 1.0)
                if "area" in peak:
                    raw["area"][peak["label"]] = (float(peak["area"]), 0.01)
                if "concentration" in peak:
                    raw["concentration"][peak["label"]] = (
                        float(peak["concentration"]),
                        float(peak["concentration"]) * 1e-3,
                    )
                if "normalizedConcentration" in peak:
                    raw["xout"][peak["label"]] = (
                        float(peak["normalizedConcentration"]),
                        float(peak["normalizedConcentration"]) * 1e-3,
                    )
                if "top" in peak:
                    raw["retention time"][peak["label"]] = (float(peak["top"]), 0.01)
        else:
            logger.warning("'analysis' of chromatogram not present in file '%s'", fn)

    valve = jsdata.get("annotations", {}).get("valcoPosition", None)
    if valve is not None:
        raw["valve"] = valve

    species = sorted(species)
    data_vars = {}
    for k, v in units.items():
        vals, devs = zip(*[raw[k].get(s, (np.nan, np.nan)) for s in species])
        data_vars[k] = (
            ["uts", "species"],
            [vals],
            {"ancillary_variables": f"{k}_std_err"},
        )
        data_vars[f"{k}_std_err"] = (
            ["uts", "species"],
            [devs],
            {"standard_name": f"{k} stdandard_error"},
        )
        if v is not None:
            data_vars[k][2]["units"] = v
            data_vars[f"{k}_std_err"][2]["units"] = v

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={"species": (["species"], species), "uts": (["uts"], [uts])},
        attrs=metadata,
    )
    return ds
