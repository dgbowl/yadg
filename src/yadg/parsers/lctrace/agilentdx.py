import zipfile
import tempfile
import os

from .agilentch import process as processch


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
    """
    Agilent OpenLab DX archive parser.

    This is a simple wrapper around the Agilent OpenLab signal trace parser in
    :mod:`yadg.parsers.lctrace.agilentch`. This wrapper first un-zips the DX
    file into a temporary directory, and then processess all CH files found
    within the archive.

    Timesteps from multiple CH files, if present, are concatenated.

    """
    zf = zipfile.ZipFile(fn)
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        chrom = []
        meta = {}
        common = None
        for ffn in os.listdir(tempdir):
            if ffn.endswith("CH"):
                _chrom, _meta, _common = processch(ffn, encoding, timezone)
                for ts in _chrom:
                    ts["fn"] = str(fn)
                    chrom.append(ts)
                if _meta is not None:
                    meta.update(_meta)
                common = _common
    return chrom, meta, common
