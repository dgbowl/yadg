"""
**fusionzip**: Processing Inficon Fusion zipped data format (zip).
------------------------------------------------------------------

This is a wrapper parser which unzips the provided zip file, and then uses
the :mod:`yadg.parsers.chromtrace.fusionjson` parser to parse every data
file present in the archive.

Exposed metadata:
`````````````````

.. code-block:: yaml

    method:   !!str
    sampleid: !!str
    version:  !!str
    datafile: !!str

.. codeauthor:: Peter Kraus
"""
import zipfile
import tempfile
import os
import xarray as xr
from datatree import DataTree

from .fusionjson import process as processjson


def process(*, fn: str, encoding: str, timezone: str, **kwargs: dict) -> DataTree:
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
    class:`datatree.DataTree`
        A :class:`datatree.DataTree` containing one :class:`xarray.Dataset` per detector. If
        multiple timesteps are found in the zip archive, the :class:`datatree.DataTrees`
        are collated along the ``uts`` dimension.

    """

    zf = zipfile.ZipFile(fn)
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        dt = None
        for ffn in sorted(os.listdir(tempdir)):
            path = os.path.join(tempdir, ffn)
            if ffn.endswith("fusion-data"):
                fdt = processjson(fn=path, encoding=encoding, timezone=timezone)
                if dt is None:
                    dt = fdt
                elif isinstance(dt, DataTree):
                    for k, v in fdt.items():
                        if k in dt:  # pylint: disable=E1135
                            newv = xr.concat(
                                [dt[k].ds, v.ds],  # pylint: disable=E1136
                                dim="uts",
                                combine_attrs="identical",
                            )
                        else:
                            newv = v.ds
                        dt[k] = DataTree(newv)  # pylint: disable=E1137
                else:
                    raise RuntimeError("We should not get here.")
    return dt
