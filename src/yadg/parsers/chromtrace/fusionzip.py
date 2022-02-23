"""
File parser for Fusion zip archive format (zip).

This is a wrapper parser which unzips the provided zip file, and then uses
the :mod:`yadg.parsers.chromtrace.fusionjson` parser to parse every data
file present in the archive.

Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      sampleid: !!str
      username: None
      version:  !!str
      valve:    !!int
      datafile: !!str

.. codeauthor:: Peter Kraus
"""
import zipfile
import tempfile
import os

from .fusionjson import process as processjson


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict]:
    """
    Fusion zip file format.

    The Fusion GC's can export their json formats as a zip archive of a folder
    of jsons. This parser allows for parsing of this zip archive directly,
    without the user having to unzip & move the data.

    Parameters
    ----------
    fn
        Filename to process.

    encoding
        Not used as the file is binary.

    timezone
        Timezone information. This should be ``"localtime"``.

    Returns
    -------
    (chroms, metadata): tuple[list, dict]
        Standard timesteps & metadata tuple.
    """

    zf = zipfile.ZipFile(fn)
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        chroms = []
        meta = {}
        for ffn in sorted(os.listdir(tempdir)):
            ffn = os.path.join(tempdir, ffn)
            if ffn.endswith("fusion-data"):
                _chrom, _meta = processjson(ffn, encoding, timezone)
                for ts in _chrom:
                    ts["fn"] = str(fn)
                    chroms.append(ts)
                if _meta is not None:
                    meta.update(_meta)
                meta["params"]["datafile"] = str(ffn)
    return chroms, meta
