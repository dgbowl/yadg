"""
File parser for Agilent OpenLab data archive files (DX).

This is a wrapper parser which unzips the provided DX file, and then uses the 
:mod:`yadg.parsers.chromtrace.agilentch` parser to parse every CH file present in
the archive. The IT files in the archive are currently ignored.

Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      sampleid: !!str
      username: !!str
      version:  !!str
      valve:    None
      datafile: !!str

In addition to the metadata exposed by the CH parser, the ``datafile`` entry
is populated with the corresponding name of the CH file. The ``fn`` entry in each
timestep contains the parent DX file.

.. note::

   Currently the timesteps from multiple CH files (if present) are appended in the
   timesteps array without any further sorting.

.. codeauthor:: Peter Kraus
"""
import zipfile
import tempfile
import os

from .agilentch import process as processch


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict]:
    """
    Agilent OpenLab DX archive parser.

    This is a simple wrapper around the Agilent OpenLab signal trace parser in
    :mod:`yadg.parsers.chromtrace.agilentch`. This wrapper first un-zips the DX
    file into a temporary directory, and then processess all CH files found
    within the archive, concatenating timesteps from multiple files.

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
        common = None
        for ffn in os.listdir(tempdir):
            if ffn.endswith("CH"):
                _chrom, _meta = processch(ffn, encoding, timezone)
                for ts in _chrom:
                    ts["fn"] = str(fn)
                    chroms.append(ts)
                if _meta is not None:
                    meta.update(_meta)
                meta["params"]["datafile"] = str(ffn)
    return chroms, meta
