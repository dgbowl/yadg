"""
**empalcxlsx**: Processing Empa's online LC exported data (xlsx)
----------------------------------------------------------------

This is a structured format produced by the export from Agilent's Online LC device
at Empa. It contains three sections:

  - metadata section,
  - table containing sampling information,
  - table containing analysed chromatography data.


Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      username: !!str
      version:  !!int
      datafile: !!str

.. codeauthor:: Peter Kraus
"""
import logging
import datetime
import openpyxl
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

logger = logging.getLogger(__name__)


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict]:
    """
    Fusion xlsx export format.

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
    ([chrom], metadata, fulldate): tuple[list, dict, bool]
        Standard timesteps, metadata, and date tuple.
    """
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
        val = row[1].value if len(row) > 1 else ""
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

    ws = wb["Page 3"]
    for row in ws.rows:
        if "Line#" in str(row[0].value):
            headers = [i.value.replace("\n", "").replace(" ", "") for i in row]
        else:
            data = [str(i.value) if i.value is not None else None for i in row]
            sn = data[headers.index("SampleName")].replace("\n", "").replace(" ", "")
            cn = data[headers.index("Compound")]

            h = data[headers.index("PeakHeight")]
            if h is not None:
                if "height" not in samples[sn]:
                    samples[sn]["height"] = {}
                n, s = tuple_fromstr(h)
                samples[sn]["height"][cn] = {"n": n, "s": s, "u": " "}

            A = data[headers.index("Area")]
            if A is not None:
                if "area" not in samples[sn]:
                    samples[sn]["area"] = {}
                n, s = tuple_fromstr(A)
                samples[sn]["area"][cn] = {"n": n, "s": s, "u": " "}

            if metadata["version"] == 2:
                c = data[headers.index("Concentration")]
                u = "mmol/l"
            else:
                logger.warning(
                    "Report version '%d' in file '%s' not understood.",
                    metadata["version"],
                    fn,
                )
                c = data[headers.index("Concentration")]
                u = "mmol/l"
            if c is not None:
                if "concentration" not in samples[sn]:
                    samples[sn]["concentration"] = {}
                n, s = tuple_fromstr(c)
                samples[sn]["concentration"][cn] = {"n": n, "s": s, "u": u}

            rt = data[headers.index("RT[min]")]
            if rt is not None:
                if "retention time" not in samples[sn]:
                    samples[sn]["retention time"] = {}
                n, s = tuple_fromstr(rt)
                samples[sn]["retention time"][cn] = {"n": n, "s": s, "u": "min"}

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
        uts = td.total_seconds()
        point = {
            "uts": uts,
            "fn": fn,
            "raw": v,
        }
        data.append(point)
    return data, {"params": metadata}, False
