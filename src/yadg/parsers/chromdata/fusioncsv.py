"""
**fusioncsv**: Processing Inficon Fusion csv export format (csv).
------------------------------------------------------------------

This is a tabulated format, including the concentrations, mole fractions, peak
areas, and retention times. The latter is ignored by this parser.

.. warning::

    As also mentioned in the ``csv`` files themselves, the use of this filetype
    is discouraged, and the ``json`` files (or a zipped archive of them) should
    be parsed instead.

.. codeauthor:: Peter Kraus
"""
import logging
from zoneinfo import ZoneInfo
from ...dgutils.dateutils import str_to_uts
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import xarray as xr
import numpy as np

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


def process(
    *, fn: str, encoding: str, timezone: ZoneInfo, **kwargs: dict
) -> xr.Dataset:
    """
    Fusion csv export format.

    Multiple chromatograms per file, with multiple detectors.

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
                "uts": str_to_uts(timestamp=f"{items[0]}{offset}", timezone=timezone),
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
        attrs=dict(method=method),
    )

    return ds
