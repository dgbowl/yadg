"""
**agilentch**: Processing Agilent OpenLab data archive files (DX).
------------------------------------------------------------------

This is a wrapper parser which unzips the provided DX file, and then uses the
:mod:`yadg.parsers.chromtrace.agilentch` parser to parse every CH file present in
the archive. The IT files in the archive are currently ignored.

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
from datatree import DataTree
import xarray as xr


def process(*, fn: str, encoding: str, timezone: str, **kwargs: dict) -> DataTree:
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
    class:`datatree.DataTree`
        A :class:`datatree.DataTree` containing one :class:`xarray.Dataset` per detector. If
        multiple timesteps are found in the zip archive, the :class:`datatree.DataTrees`
        are collated along the ``uts`` dimension.

    """

    zf = zipfile.ZipFile(fn)
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        dt = None
        for ffn in os.listdir(tempdir):
            if ffn.endswith("CH"):
                path = os.path.join(tempdir, ffn)
                fdt = processch(fn=path, encoding=encoding, timezone=timezone)
                if dt is None:
                    dt = fdt
                elif isinstance(dt, DataTree):
                    for k, v in fdt.items():
                        if k in dt:  # pylint: disable=E1135
                            try:
                                newv = xr.concat(
                                    [dt[k].ds, v.ds],  # pylint: disable=E1136
                                    dim="uts",
                                    combine_attrs="identical",
                                )
                            except xr.MergeError:
                                raise RuntimeError(
                                    "Merging metadata from the unzipped agilent-ch files has failed. "
                                    "This is a bug. Please open an issue on GitHub."
                                )
                        else:
                            newv = v.ds
                        dt[k] = DataTree(newv)  # pylint: disable=E1137
                else:
                    raise RuntimeError("We should not get here.")
    return dt
