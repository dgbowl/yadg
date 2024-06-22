"""
For processing Inficon Fusion csv export format (csv). This is a tabulated format,
including the concentrations, mole fractions, peak areas, and retention times.

.. warning::

    As also mentioned in the ``csv`` files themselves, the use of this filetype
    is discouraged, and the ``json`` files (or a zipped archive of them) should
    be parsed instead.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Fusion_csv

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:                !!float               # Unix timestamp
        species:            !!str                 # Species name
      data_vars:
        area:               (uts, species)        # Integrated peak area
        concentration:      (uts, species)        # Calibrated peak area
        xout:               (uts, species)        # Mole fraction (normalised conc.)
        retention time:     (uts, species)        # Retention time

Metadata
````````
The following metadata is extracted:

    - ``method``: Name of the chromatographic method.

Uncertainties
`````````````
The uncertainties are derived from the string representation of the floats.

.. codeauthor::
    Peter Kraus

"""

import logging
import numpy as np
import xarray as xr
from datatree import DataTree
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

from yadg import dgutils


logger = logging.getLogger(__name__)

data_names = {
    "Concentration": "concentration",
    "NormalizedConcentration": "xout",
    "Area": "area",
    "RT(s)": "retention time",
}

data_units = {
    "concentration": "%",
    "xout": "%",
    "area": None,
    "retention time": "s",
}


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()

    data = []
    species = set()
    for line in lines[3:]:
        if "SampleName" in line:
            header = [i.strip() for i in line.split(",")]
            sni = header.index("SampleName")
            method = header[0]
            for ii, i in enumerate(header):
                if i == "":
                    header[ii] = header[ii - 1]
        elif "Detectors" in line:
            detectors = [i.replace('"', "").strip() for i in line.split(",")]
            for ii, i in enumerate(detectors):
                if i == "":
                    detectors[ii] = detectors[ii - 1]
        elif "Time" in line:
            samples = [i.replace('"', "").strip() for i in line.split(",")]
            time = samples[0]
            if time == "Time (GMT 120 mins)":
                offset = "+02:00"
            elif time == "Time (GMT 60 mins)":
                offset = "+01:00"
            else:
                logger.error("offset '%s' not understood", time)
                offset = "+00:00"
        elif "% RSD" in line:
            continue
        else:
            items = line.split(",")
            point = {
                "concentration": {},
                "xout": {},
                "area": {},
                "retention time": {},
                "sampleid": items[sni],
                "uts": dgutils.str_to_uts(
                    timestamp=f"{items[0]}{offset}", timezone=timezone
                ),
            }
            for ii, i in enumerate(items[2:]):
                ii += 2
                species.add(samples[ii])
                point[data_names[header[ii]]][samples[ii]] = tuple_fromstr(i)
            data.append(point)

    species = sorted(species)
    data_vars = {}
    for kk in {"concentration", "xout", "area", "retention time"}:
        vals = []
        devs = []
        for i in range(len(data)):
            ivals, idevs = zip(
                *[data[i][kk].get(cn, (np.nan, np.nan)) for cn in species]
            )
            vals.append(ivals)
            devs.append(idevs)
        data_vars[kk] = (
            ["uts", "species"],
            vals,
            {"anciliary_variables": f"{kk}_std_err"},
        )
        data_vars[f"{kk}_std_err"] = (
            ["uts", "species"],
            devs,
            {"standard_name": f"{kk} standard_error"},
        )
        if data_units[kk] is not None:
            data_vars[kk][2]["units"] = data_units[kk]
            data_vars[f"{kk}_std_err"][2]["units"] = data_units[kk]

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={
            "species": (["species"], species),
            "uts": (["uts"], [i["uts"] for i in data]),
        },
        attrs=dict(original_metadata=dict(method=method)),
    )

    return DataTree(ds)
