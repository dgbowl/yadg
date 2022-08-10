"""
**fusioncsv**: Processing Inficon Fusion csv export format (csv).
------------------------------------------------------------------

This is a tabulated format, including the concentrations, mole fractions, peak 
areas, and retention times. The latter is ignored by this parser.

.. warning::

    As also mentioned in the ``csv`` files themselves, the use of this filetype
    is discouraged, and the ``json`` files (or a zipped archive of them) should
    be parsed instead.


Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      username: None
      version:  None
      datafile: None

.. codeauthor:: Peter Kraus
"""
import logging
from ...dgutils.dateutils import str_to_uts
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

logger = logging.getLogger(__name__)

_headers = {
    "Concentration": ["concentration", "%"],
    "NormalizedConcentration": ["xout", "%"],
    "Area": ["area", " "],
    "RT(s)": ["retention time", "s"],
}


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

    data = []
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
            }
            uts = str_to_uts(f"{items[0]}{offset}", timezone=timezone)
            for ii, i in enumerate(items[2:]):
                ii += 2
                h = _headers.get(header[ii], None)
                chem = samples[ii]
                if h is None:
                    continue
                n, s = tuple_fromstr(i)
                point[h[0]][chem] = {
                    "n": n,
                    "s": s,
                    "u": h[1],
                }
            data.append({"uts": uts, "raw": point, "fn": fn})
    return data, {"params": {"method": method}}, True
