"""
**empalccsv**: Processing Empa's online LC exported data (csv)
--------------------------------------------------------------

This is a structured format produced by the export from Agilent's Online LC device
at Empa. It contains three sections:

  - metadata section,
  - table containing sampling information,
  - table containing analysed chromatography data.

.. codeauthor:: Peter Kraus
"""
import logging
import datetime
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import xarray as xr
import numpy as np

logger = logging.getLogger(__name__)


def process(*, fn: str, encoding: str, **kwargs: dict) -> xr.Dataset:
    """
    Custom Agilent Online LC csv export format.

    Multiple chromatograms per file, with multiple detectors.

    Parameters
    ----------
    fn
        Filename to process.

    encoding
        Encoding used to open the file.

    Returns
    -------
    :class:`xarray.Dataset`

    """

    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()

    metadata = {}
    while len(lines) > 0:
        line = lines.pop(0)
        if len(lines) == 0:
            raise RuntimeError(
                f"Last line of file '{fn}' read during metadata section."
            )
        elif line.strip() == "":
            break
        elif line.strip().startswith("Sequence name"):
            metadata["sequence"] = line.split(":,")[1]
        elif line.strip().startswith("Description"):
            metadata["description"] = line.split(":,")[1]
        elif line.strip().startswith("Acquired by"):
            metadata["username"] = line.split(":,")[1]
        elif line.strip().startswith("Data path"):
            metadata["datafile"] = line.split(":,")[1]
        elif line.strip().startswith("Report version"):
            metadata["version"] = int(line.split(":,")[1])

    if metadata.get("version", None) is None:
        raise RuntimeError(f"Report version in file '{fn}' was not specified.")

    samples = {}
    while len(lines) > 0:
        line = lines.pop(0)
        if len(lines) == 0:
            raise RuntimeError(f"Last line of file '{fn}' read during samples section.")
        elif line.strip() == "":
            break
        elif "Line#" in line:
            headers = [i.strip() for i in line.split(",")]
        else:
            data = [i.strip() for i in line.split(",")]
            sample = {
                "location": data[headers.index("Location")],
                "injection date": data[headers.index("Injection Date")],
                "acquisition": {
                    "method": data[headers.index("Acq Method Name")],
                    "version": data[headers.index("Acq Method Version")],
                },
                "integration": {
                    "method": data[headers.index("Injection DA Method Name")],
                    "version": data[headers.index("Injection DA Method Version")],
                },
                "offset": data[headers.index("Time offset")],
            }
            if sample["offset"] != "":
                sn = data[headers.index("Sample Name")]
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

    metadata["method"] = r["acquisition"]["method"]

    species = set()
    while len(lines) > 0:
        line = lines.pop(0)
        if len(lines) == 0:
            break
        elif line.strip() == "":
            break
        elif "Line#" in line:
            headers = [i.strip() for i in line.split(",")]
        else:
            data = [i.strip() for i in line.split(",")]
            sn = data[headers.index("Sample Name")]
            cn = data[headers.index("Compound")]
            species.add(cn)

            h = data[headers.index("Peak Height")]
            if h != "":
                if "height" not in samples[sn]:
                    samples[sn]["height"] = {}
                samples[sn]["height"][cn] = tuple_fromstr(h)

            A = data[headers.index("Area")]
            if A != "":
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
            if c != "":
                if "concentration" not in samples[sn]:
                    samples[sn]["concentration"] = {}
                samples[sn]["concentration"][cn] = tuple_fromstr(c)

            rt = data[headers.index("RT [min]")]
            if rt != "":
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
        attrs=metadata,
    )

    return ds
