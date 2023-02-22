"""
**eclabmpt**: Processing of BioLogic's EC-Lab ASCII export files.
-----------------------------------------------------------------

``.mpt`` files are made up of a header portion (with the technique
parameter sequences and an optional loops section) and a tab-separated
data table.

A list of techniques supported by this parser is shown in `the techniques table
<yadg.parsers.electrochem.eclabmpr.techniques>`_.

File Structure of ``.mpt`` Files
````````````````````````````````

These human-readable files are sectioned into headerlines and datalines.
The header part of the ``.mpt`` files is made up of information that can be found
in the settings, log and loop modules of the binary ``.mpr`` file.

If no header is present, the timestamps will instead be calculated from
the file's ``mtime()``.


Metadata
````````
The metadata will contain the information from the header of the file.

.. note ::

    The mapping between metadata parameters between ``.mpr`` and ``.mpt`` files
    is not yet complete.

.. codeauthor:: Nicolas Vetsch
"""

from zoneinfo import ZoneInfo
from pathlib import Path
from dgbowl_schemas.yadg import FileType
import logging
import pandas as pd
from .extractor import process

logger = logging.getLogger(__name__)

supports = {
    "eclab.mpt",
    "marda:biologic-mpt",
}


def extract(
    path: Path,
    filetype: FileType,
) -> tuple[dict, pd.DataFrame, pd.DataFrame, dict]:

    metadata, nominal, sigma, units = process(
        fn=str(path),
        encoding=filetype.encoding,
        timezone=ZoneInfo(filetype.timezone),
    )

    return metadata, nominal, sigma, units


