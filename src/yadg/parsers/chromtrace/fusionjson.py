"""
**fusionjson**: Processing Inficon Fusion json data format (json).
------------------------------------------------------------------

This is a fairly detailed data format, including the traces, the calibration applied,
and also the integrated peak areas. If the peak areas are present, this is returned
in the list of timesteps as a ``"peaks"`` entry.

Exposed metadata:
`````````````````

.. code-block:: yaml

    method:   !!str
    sampleid: !!str
    version:  !!str
    datafile: !!str

.. codeauthor:: Peter Kraus
"""
import json
from zoneinfo import ZoneInfo
import numpy as np
from ...dgutils.dateutils import str_to_uts
import xarray as xr
from datatree import DataTree


def process(*, fn: str, encoding: str, timezone: ZoneInfo, **kwargs: dict) -> DataTree:
    """
    Fusion json format.

    One chromatogram per file with multiple traces, and integrated peak areas.

    .. warning::

        To parse the integrated data present in these files, use the
        :mod:`~yadg.parsers.chromdata` parser.

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
    class:`datatree.DataTree`
        A :class:`datatree.DataTree` containing one :class:`xarray.Dataset` per detector.

    """

    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        jsdata = json.load(infile)
    metadata = {
        "method": jsdata.get("methodName", "n/a"),
        "sampleid": jsdata.get("annotations", {}).get("name", None),
        "version": jsdata.get("softwareVersion", {}).get("version", None),
        "datafile": jsdata.get("sequence", {}).get("location", None),
    }
    uts = str_to_uts(timestamp=jsdata["runTimeStamp"], timezone=timezone)

    # sort detector keys to ensure alphabetic order for ID matching
    traces = sorted(jsdata["detectors"].keys())
    vals = {}
    for detname in traces:
        detdict = jsdata["detectors"][detname]
        fvals = xr.Dataset(
            data_vars={
                "signal": (
                    ["uts", "elution_time"],
                    [detdict["values"]],
                    {"ancillary_variables": "signal_std_err"},
                ),
                "signal_std_err": (
                    ["uts", "elution_time"],
                    [np.ones(detdict["nValuesExpected"])],
                    {"standard_name": "signal standard_error"},
                ),
                "elution_time_std_err": (
                    ["elution_time"],
                    np.ones(detdict["nValuesExpected"]) / detdict["nValuesPerSecond"],
                    {"units": "s", "standard_name": "elution_time standard_error"},
                ),
            },
            coords={
                "elution_time": (
                    ["elution_time"],
                    np.arange(detdict["nValuesExpected"]) / detdict["nValuesPerSecond"],
                    {"units": "s", "ancillary_variables": "elution_time_std_err"},
                ),
                "uts": (["uts"], [uts]),
            },
            attrs={},
        )
        valve = jsdata.get("annotations", {}).get("valcoPosition", None)
        if valve is not None:
            fvals["valve"] = valve
        vals[detname] = fvals

    dt = DataTree.from_dict(vals)
    dt.attrs = metadata
    return dt
