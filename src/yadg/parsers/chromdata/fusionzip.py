"""
**fusionzip**: Processing Inficon Fusion zipped data format (zip).
------------------------------------------------------------------

This is a wrapper parser which unzips the provided zip file, and then uses
the :mod:`yadg.parsers.chromdata.fusionjson` parser to parse every data
file present in the archive.

.. codeauthor:: Peter Kraus
"""
import zipfile
import tempfile
import os
import xarray as xr

from .fusionjson import process as processjson


def process(*, fn: str, encoding: str, timezone: str, **kwargs: dict) -> xr.Dataset:
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
    :class:`xarray.Dataset`
        The data from the inidividual json files contained in the zip archive are
        concatenated into a single :class:`xarray.Dataset`. This might fail if the metadata
        in the json files differs, or if the dimensions are not easily concatenable.

    """

    zf = zipfile.ZipFile(fn)
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        ds = None
        for ffn in sorted(os.listdir(tempdir)):
            ffn = os.path.join(tempdir, ffn)
            if ffn.endswith("fusion-data"):
                ids = processjson(fn=ffn, encoding=encoding, timezone=timezone)
                if ds is None:
                    ds = ids
                else:
                    try:
                        ds = xr.concat([ds, ids], dim="uts", combine_attrs="identical")
                    except xr.MergeError:
                        raise RuntimeError(
                            "Merging metadata from the unzipped fusion-json files has failed. "
                            "This might be caused by trying to parse data obtained using "
                            "different chromatographic methods. Please check the contents "
                            "of the unzipped files."
                        )
    return ds
