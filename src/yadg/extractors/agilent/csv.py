"""
Extractor of Agilent Chemstation Chromtab tabulated data files. This file format may
include multiple timesteps consisting of several traces each in a single CSV file. It
contains a header section for each timestep, followed by a detector name, and a sequence
of "X, Y" datapoints, which are stored as ``elution_time`` and ``signal``.

.. warning ::

    It is not guaranteed that the X-axis of the chromatogram (i.e. ``elution_time``) is
    consistent between the timesteps of the same trace. The traces are expanded to the
    length of the longest trace, and the shorter traces are padded with ``NaNs``.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.Agilent_csv

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
      {{ detector_name }}:
        coords:
          uts:            !!float               # Unix timestamp
          elution_time:   !!float               # Elution time
        data_vars:
          signal:         (uts, elution_time)   # Signal data

Uncertainties
`````````````
- all values: string to float conversion

Metadata
````````
The following metadata is extracted:

    - ``sampleid``: Sample name.
    - ``datafile``: Original path of the data file.


.. codeauthor::
    Peter Kraus

"""

import logging
import xarray as xr
from pathlib import Path
from xarray import DataTree, Dataset
from yadg import dgutils
from yadg.dgutils.table import process_table
from yadg.extractors import get_extract_dispatch

logger = logging.getLogger(__name__)
extract = get_extract_dispatch()


def process_headers(headers: list, columns: list, timezone: str) -> tuple[dict, float]:
    orig_meta = {k: v.strip() for k, v in zip(headers, columns)}
    if "Date Acquired" in orig_meta:
        uts = dgutils.str_to_uts(
            timestamp=columns[headers.index("Date Acquired")].strip(),
            format="%d %b %Y %H:%M",
            timezone=timezone,
        )
    else:
        logger.warning("'Date Acquired' not in file header, cannot infer timestamp.")
        uts = None
    return orig_meta, uts


def process_trace(lines: list[str], uts: float) -> Dataset:
    data_vars = process_table(
        lines=lines,
        headers=["elution_time", "signal"],
        sep=",",
    )
    data_vars["elution_time"] = (
        data_vars["elution_time"][0],
        [v * 60.0 for v in data_vars["elution_time"][1]],
        data_vars["elution_time"][2],
    )
    data_vars["elution_time"][2]["units"] = "s"
    data_vars["elution_time_uncertainty"] = (
        [],
        data_vars["elution_time_uncertainty"][1] * 60,
        data_vars["elution_time_uncertainty"][2],
    )
    coords = dict(
        elution_time=data_vars.pop("elution_time"),
        uts=(("uts",), [uts]),
    )
    data_vars["signal"] = (
        ("uts", "elution_time"),
        [data_vars["signal"][1]],
        data_vars["signal"][2],
    )
    ds = Dataset(data_vars=data_vars, coords=coords)
    return ds


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(source, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()
    orig_meta = {}
    tstart = 0
    tend = 0
    dtdict = {}
    uts = None
    utsnext = None
    detname = None
    for li, line in enumerate(lines):
        # process headers etc.
        if '"' in line:
            parts = line.strip().split(",")
            if len(parts) == 1:
                if tstart != tend:
                    ds = process_trace(lines[tstart : tend + 1], uts)
                    dtdict[detname].append(ds)
                uts = utsnext
                detname = parts[0].replace('"', "").split("\\")[-1]
                if detname not in dtdict:
                    dtdict[detname] = []
                tstart = li + 1
                tend = tstart
            elif len(parts) > 2:
                if '"Date Acquired"' in parts:
                    headers = [p.replace('"', "") for p in parts]
                else:
                    columns = [p.replace('"', "") for p in parts]
                    thismeta, utsnext = process_headers(headers, columns, timezone)
                    dgutils.merge_meta(orig_meta, thismeta)
        else:
            tend = li
    if tstart != tend:
        ds = process_trace(lines[tstart : tend + 1], uts)
        dtdict[detname].append(ds)

    dt = {}
    for detname, dsets in dtdict.items():
        dt[detname] = xr.concat(
            dsets,
            dim="uts",
            data_vars="different",
            compat="identical",
            join="outer",
        )
    dt = DataTree.from_dict(dt)
    dt.attrs = {"original_metadata": orig_meta}
    return dt
