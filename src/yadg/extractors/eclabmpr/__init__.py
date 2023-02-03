from zoneinfo import ZoneInfo
from pathlib import Path
from dgbowl_schemas.yadg import FileType
import logging

from ...parsers.electrochem.eclabmpr import process

logger = logging.getLogger(__name__)

supports = {
    "eclab.mpr",
    "marda:biologic-mpr",
}


def extract(
    path: Path,
    filetype: FileType,
) -> tuple[list, dict, bool]:

    data, metadata, _ = process(
        fn=str(path),
        encoding=filetype.encoding,
        timezone=ZoneInfo(filetype.timezone),
    )

    return metadata, data
