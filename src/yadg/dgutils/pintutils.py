import logging
from typing import Union
import pint

ureg = pint.UnitRegistry(preprocessors=[
    lambda s: s.replace('%%', ' permille '),
    lambda s: s.replace('%', ' percent ')
])

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

def sanitize_units(units: Union[str, dict[str], list[str]]) -> None:
    if isinstance(units, list):
        for i in range(len(units)):
            units[i] = _sanitize_helper(units[i])
    elif isinstance(units, dict):
        for k, v in units.items():
            units[k] = _sanitize_helper(v)
    elif isinstance(units, str):
        units = _sanitize_helper(units)
    else:
        logging.error(
            "sanitize_units: Supplied type of 'units' not understood: '{type(units)}'"
        )