"""
**empalccsv**: Processing Empa's online LC exported data (csv)
--------------------------------------------------------------

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
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

logger = logging.getLogger(__name__)


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict]:
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
    ([chrom], metadata, fulldate): tuple[list, dict, bool]
        Standard timesteps, metadata, and date tuple.
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

            h = data[headers.index("Peak Height")]
            if h != "":
                if "height" not in samples[sn]:
                    samples[sn]["height"] = {}
                n, s = tuple_fromstr(h)
                samples[sn]["height"][cn] = {"n": n, "s": s, "u": " "}

            A = data[headers.index("Area")]
            if A != "":
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
            if c != "":
                if "concentration" not in samples[sn]:
                    samples[sn]["concentration"] = {}
                n, s = tuple_fromstr(c)
                samples[sn]["concentration"][cn] = {"n": n, "s": s, "u": u}

            rt = data[headers.index("RT [min]")]
            if rt != "":
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
