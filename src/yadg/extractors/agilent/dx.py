"""
Extractor of Agilent OpenLab DX archives. This is a wrapper parser which unzips the
provided DX file, and then uses the :mod:`yadg.extractors.agilent.ch` extractor
to parse every CH file present in the archive. The IT files in the archive are currently
ignored.

.. note::

   Currently the timesteps from multiple CH files (if present) are appended in the
   timesteps array without any further sorting.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Agilent_dx

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      {{ detector_name }}:
        coords:
          uts:            !!float               # Unix timestamp
          elution_time:   !!float               # Elution time
        data_vars:
          signal:         (uts, elution_time)   # Signal data

Metadata
````````
The following metadata is extracted:

    - ``sampleid``: Sample name.
    - ``username``: User name used to generate the file.
    - ``method``: Name of the chromatographic method.
    - ``version``: Version of the CH file (only "179" is currently supported.)

.. codeauthor::
    Peter Kraus

"""

import zipfile
import tempfile
import os
from datatree import DataTree

from yadg.extractors.agilent.ch import extract as extract_ch
from yadg import dgutils


def extract(
    *,
    fn: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    zf = zipfile.ZipFile(fn)
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        dt = None
        filenames = [ffn for ffn in os.listdir(tempdir) if ffn.endswith("CH")]
        for ffn in sorted(filenames):
            path = os.path.join(tempdir, ffn)
            fdt = extract_ch(fn=path, timezone=timezone, **kwargs)
            dt = dgutils.merge_dicttrees(dt, fdt.to_dict(), "identical")
    return DataTree.from_dict(dt)
