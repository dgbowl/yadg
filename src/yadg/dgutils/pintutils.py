"""
``pint`` compatibility functions in **yadg**.

This module contains the unit sanitizer to make some common unit spelling
variants compatible with :mod:`pint`.
"""

import logging

logger = logging.getLogger(__name__)

def _sanitize_helper(unit: str) -> str:
    unit = unit.replace("Bar", "bar")
    if unit in {"deg C", "Deg C"}:
        return "degC"
    else:
        return unit


def sanitize_units(
    units: str | dict[str, str] | list[str],
) -> str | dict[str, str] | list[str]:
    """
    Unit sanitizer.

    This sanitizer should be used where user-supplied units are likely to occur,
    such as in the parsers :mod:`yadg.extractors.basic.csv`. Currently, only two
    replacements are done:

      - "Bar" is replaced with "bar"
      - "Deg C" is replaced with "degC

    Use with caution.

    Parameters
    ----------
    units
        Object containing string units.

    """
    if isinstance(units, list):
        units = [_sanitize_helper(i) for i in units]
    elif isinstance(units, dict):
        units = {k: _sanitize_helper(v) for k, v in units.items()}
    elif isinstance(units, str):
        units = _sanitize_helper(units)
    else:
        logger.error("Supplied type of 'units' not understood: '%s'", str(type(units)))
    return units
