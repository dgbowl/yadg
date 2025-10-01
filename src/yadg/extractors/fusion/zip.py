"""
For processing Inficon Fusion zipped data. This is a wrapper parser which unzips the
provided zip file, and then uses the :mod:`yadg.extractors.fusion.json` extractor
to parse every fusion-data file present in the archive.

Contains both the data from the raw chromatogram and the post-processed results.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.Fusion_zip

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
      coords:
        uts:              !!float
        species:          !!str
      data_vars:
        height:           (uts, species)        # Peak height at maximum
        area:             (uts, species)        # Integrated peak area
        concentration:    (uts, species)        # Calibrated peak area
        xout:             (uts, species)        # Mole fraction (normalized conc.)
        retention time:   (uts, species)        # Peak retention time
      {{ detector_name }}:
        coords:
          uts:            !!float               # Unix timestamp
          elution_time:   !!float               # Elution time
        data_vars:
          signal:         (uts, elution_time)   # Signal data
          valve:          (uts)                 # Valve position

Metadata
````````
No metadata is currently extracted.

.. codeauthor::
    Peter Kraus

"""

import zipfile
import tempfile
import os
from xarray import DataTree
from yadg.extractors.fusion.json import extract as extract_json
from yadg import dgutils
from pathlib import Path
from yadg.extractors import get_extract_dispatch
import logging

extract = get_extract_dispatch()
logger = logging.getLogger(__name__)


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    timezone: str,
    encoding: str,
    **kwargs: dict,
) -> DataTree:
    zf = zipfile.ZipFile(source)
    strict_merge = not kwargs.get("ignore_merge_errors", False)
    if strict_merge is False:
        logger.info("Will drop metadata conflicts in individual fusion-data files.")

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        dt = None
        filenames = [ffn for ffn in os.listdir(tempdir) if ffn.endswith("fusion-data")]
        for ffn in sorted(filenames):
            logger.debug("Processing filename '%s'", ffn)
            path = Path(tempdir) / ffn
            fdt = extract_json(
                source=path, timezone=timezone, encoding=encoding, **kwargs
            )
            dt = dgutils.merge_dicttrees(dt, fdt.to_dict(), strict_merge)
    return DataTree.from_dict(dt)
