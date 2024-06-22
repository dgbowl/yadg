"""
Handles processing of the xlsx version of the structured format produced by Agilent's
Online LC device at Empa. It contains three sections:

  - metadata section,
  - table containing sampling information,
  - table containing analysed chromatography data.

Usage
`````
Available since ``yadg-4.2``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.EmpaLC_xlsx

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:            !!float               # Unix timestamp
        species:        !!str                 # Species name
      data_vars:
        height:         (uts, species)        # Peak height
        area:           (uts, species)        # Integrated peak area
        concentration:  (uts, species)        # Peak area with calibration applied
        retention time: (uts, species)        # Position of peak maximum

Metadata
````````
The following metadata is extracted:

  - ``sequence``: Sample / sequence name.
  - ``description``: A free-form description of the experiment.
  - ``username``: User name used to generate the file.
  - ``datafile``: Original path of the result file.
  - ``version``: Version of the export function used to generate the file.

.. codeauthor::
    Peter Kraus

"""

import logging
import datetime
import openpyxl
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import xarray as xr
from datatree import DataTree
import numpy as np

logger = logging.getLogger(__name__)


def extract(
    *,
    fn: str,
    **kwargs: dict,
) -> DataTree:
    try:
        wb = openpyxl.load_workbook(
            filename=fn,
            read_only=True,
        )
    except TypeError:
        raise RuntimeError(
            f"Could not read the file '{fn}' using openpyxl. Try to open and save the "
            f"file in Excel."
        )

    ws = wb["Page 1"]
    metadata = {}
    for row in ws.rows:
        val = row[1].value if len(row) > 1 and row[1].value is not None else ""
        if row[0].value.startswith("Sequence name"):
            metadata["sequence"] = val
        elif row[0].value.startswith("Description"):
            metadata["description"] = val
        elif row[0].value.startswith("Acquired by"):
            metadata["username"] = val
        elif row[0].value.startswith("Data path"):
            metadata["datafile"] = val
        elif row[0].value.startswith("Report version"):
            metadata["version"] = int(val)

    if metadata.get("version", None) is None:
        raise RuntimeError(f"Report version in file '{fn}' was not specified.")

    ws = wb["Page 2"]
    samples = {}
    for row in ws.rows:
        if "Line#" in row[0].value:
            headers = [i.value.replace("\n", "").replace(" ", "") for i in row]
        else:
            data = [str(i.value) if i.value is not None else None for i in row]
            sample = {
                "location": data[headers.index("Location")],
                "injection date": data[headers.index("InjectionDate")],
                "acquisition": {
                    "method": data[headers.index("AcqMethodName")],
                    "version": data[headers.index("AcqMethodVersion")],
                },
                "integration": {
                    "method": data[headers.index("InjectionDAMethodName")],
                    "version": data[headers.index("InjectionDAMethodVersion")],
                },
                "offset": data[headers.index("Timeoffset")],
            }
            if sample["offset"] is not None:
                sn = data[headers.index("SampleName")]
                sn = sn.replace(" ", "").replace("\n", "")
                samples[sn] = sample

    svals = samples.values()
    if len(svals) == 0:
        raise RuntimeError(
            f"No complete sample data found in file '{fn}'. "
            "Have you added time offsets?"
        )
    r = next(iter(svals))
    # check that acquisition and integration methods are consistent throughout file:
    if any([s["acquisition"]["method"] != r["acquisition"]["method"] for s in svals]):
        logger.warning("Acquisition method is inconsistent in file '%s'.", fn)
    if any([s["integration"]["method"] != r["integration"]["method"] for s in svals]):
        logger.warning("Integration method is inconsistent in file '%s'.", fn)

    metadata["method"] = r["acquisition"]["method"].replace("\n", "").replace(" ", "")

    species = set()
    ws = wb["Page 3"]
    for row in ws.rows:
        if "Line#" in str(row[0].value):
            headers = [i.value.replace("\n", "").replace(" ", "") for i in row]
        else:
            data = [str(i.value) if i.value is not None else None for i in row]
            sn = data[headers.index("SampleName")].replace("\n", "").replace(" ", "")
            cn = data[headers.index("Compound")]
            species.add(cn)

            h = data[headers.index("PeakHeight")]
            if h is not None:
                if "height" not in samples[sn]:
                    samples[sn]["height"] = {}
                samples[sn]["height"][cn] = tuple_fromstr(h)

            A = data[headers.index("Area")]
            if A is not None:
                if "area" not in samples[sn]:
                    samples[sn]["area"] = {}
                samples[sn]["area"][cn] = tuple_fromstr(A)

            if metadata["version"] == 2:
                c = data[headers.index("Concentration")]
            else:
                logger.warning(
                    "Report version '%d' in file '%s' not understood.",
                    metadata["version"],
                    fn,
                )
                c = data[headers.index("Concentration")]
            if c is not None:
                if "concentration" not in samples[sn]:
                    samples[sn]["concentration"] = {}
                samples[sn]["concentration"][cn] = tuple_fromstr(c)

            rt = data[headers.index("RT[min]")]
            if rt is not None:
                if "retention time" not in samples[sn]:
                    samples[sn]["retention time"] = {}
                samples[sn]["retention time"][cn] = tuple_fromstr(rt)

    units = {
        "height": None,
        "area": None,
        "concentration": "mmol/l",
        "retention time": "min",
    }
    species = sorted(species)
    data = []
    for k, v in samples.items():
        # Remove unnecessary parameters
        del v["acquisition"]
        del v["integration"]
        v["sampleid"] = k
        # Process offset to uts
        offset = v.pop("offset")
        t = None
        for fmt in {"%H:%M:%S"}:
            try:
                t = datetime.datetime.strptime(offset, fmt)
            except ValueError:
                continue
        if t is None:
            try:
                td = datetime.timedelta(minutes=float(offset))
            except ValueError:
                raise RuntimeError(
                    f"It was not possible to parse offset '{offset}' present in file "
                    f"'{fn}' using known formats."
                )
        else:
            td = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        point = {"uts": td.total_seconds()}
        vals = {}
        devs = {}
        for kk in {"height", "area", "concentration", "retention time"}:
            val = v.get(kk, {})
            vals[kk], devs[kk] = zip(*[val.get(cn, (np.nan, np.nan)) for cn in species])
        point["vals"] = vals
        point["devs"] = devs
        data.append(point)

    data_vars = {}
    for kk in {"height", "area", "concentration", "retention time"}:
        data_vars[kk] = (
            ["uts", "species"],
            [i["vals"][kk] for i in data],
            {"anciliary_variables": f"{kk}_std_err"},
        )
        data_vars[f"{kk}_std_err"] = (
            ["uts", "species"],
            [i["devs"][kk] for i in data],
            {"standard_name": f"{kk} standard_error"},
        )
        if units[kk] is not None:
            data_vars[kk][2]["units"] = units[kk]
            data_vars[f"{kk}_std_err"][2]["units"] = units[kk]

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={
            "species": (["species"], species),
            "uts": (["uts"], [i["uts"] for i in data]),
        },
        attrs=dict(original_metadata=metadata),
    )

    return DataTree(ds)
