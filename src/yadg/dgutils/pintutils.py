"""
``pint`` compatibility functions in **yadg**.

This package defines ``ureg``, a :class:`pint.UnitRegistry` used for validation of
`datagrams` in **yadg**. The default SI :class:`pint.UnitRegistry` is extended
by definitions of fractional quantities (%, ppm, etc.), standard volumetric
quantities (smL/min, sccm), and other dimensionless "units" present in several
file types.
"""

import logging
from typing import Union
import pint

logger = logging.getLogger(__name__)

ureg = pint.UnitRegistry(
    preprocessors=[
        lambda s: s.replace("%%", " permille "),
        lambda s: s.replace("%", " percent "),
    ]
)

definitions = """
parts_per_hundred = 1e-2 count = percent
parts_per_thousand = 1e-3 count = ‰ = promile = permille
parts_per_million = 1e-6 count = ppm
parts_per_billion = 1e-9 count = ppb

standard_milliliter = milliliter = smL
standard_liter = liter = sL
standard_cubic_centimeter_minute = cm^3/min = sccm

refractive_index_units = [] = RIU
"""

for line in definitions.split("\n"):
    line = line.strip()
    if len(line) > 0 and not line.startswith("#"):
        ureg.define(line)


def _sanitize_helper(unit: str) -> str:
    unit = unit.replace("Bar", "bar")
    if unit in ["deg C", "Deg C"]:
        return "degC"
    else:
        return unit


def sanitize_units(
    units: Union[str, dict[str, str], list[str]],
) -> Union[str, dict[str, str], list[str]]:
    """
    Unit sanitizer.

    This sanitizer should be used where user-supplied units are likely to occur,
    such as in the parsers :mod:`yadg.extractors.basic.csv`. Currently, only two
    replacements are done:

      - "Bar" is replaced with "bar"
      - "Deg C" is replace with "degC

    Use with caution.

    Parameters
    ----------
    units
        Object containing string units.

    """
    if isinstance(units, list):
        for i in range(len(units)):
            units[i] = _sanitize_helper(units[i])
    elif isinstance(units, dict):
        for k, v in units.items():
            units[k] = _sanitize_helper(v)
    elif isinstance(units, str):
        units = _sanitize_helper(units)
    else:
        logger.error("Supplied type of 'units' not understood: '%s'", str(type(units)))
    return units
