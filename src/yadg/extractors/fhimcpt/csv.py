"""
This parser handles the reading and processing of the legacy log files created by
the LabView interface for the MCPT instrument at FHI, now FU Berlin. These files contain
information about the timestamp, temperatures, and inlet / process flows.

Usage
`````
Available since ``yadg-3.0``. Deprecated since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.FHI_csv

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:            !!float     # Unix timestamp
      data_vars:
        T_f:            (uts)       # Flow temperature
        T_fs:           (uts)       # Flow temperature setpoint
        T_fo:           (uts)       # Flow heater duty cycle
        T_c:            (uts)       # Cavity temperature
        T_cs:           (uts)       # Cavity temperature setpoint
        T_co:           (uts)       # Cavity cooling duty cycle
        T_cal:          (uts)       # Calibration thermocouple temperature
        N2:             (uts)       # N2 flow
        O2:             (uts)       # N2 flow
        alkane:         (uts)       # alkane flow
        CO_CO2:         (uts)       # CO or CO2 flow
        saturator:      (uts)       # saturator flow
        pressure:       (uts)       # Reactor flow meter back-pressure
        flow low:       (uts)       # Reactor mix high-flow MFC
        flow high:      (uts)       # Reactor mix low-flow MFC
        cavity flush:   (uts)       # Cavity N2 flow
        heater flow:    (uts)       # Heater flow

Metadata
````````
No metadata is returned.

.. codeauthor::
    Peter Kraus

"""

import logging
from pydantic import BaseModel
from yadg.extractors.basic.csv import process_row
from yadg import dgutils
from datatree import DataTree

logger = logging.getLogger(__name__)


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    parameters: BaseModel,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "r", encoding=encoding) as infile:
        lines = [i.strip() for i in infile.readlines()]

    headers = [i.strip() for i in lines.pop(0).split(";")]

    for hi, header in enumerate(headers):
        if "/" in header:
            logger.warning("Replacing '/' for '_' in header '%s'.", header)
            headers[hi] = header.replace("/", "_")

    _units = [i.strip() for i in lines.pop(0).split(";")]
    units = {}
    for h in headers:
        units[h] = _units.pop(0)

    units = dgutils.sanitize_units(units)

    datecolumns, datefunc, fulldate = dgutils.infer_timestamp_from(
        spec=parameters.timestamp,
        timezone=timezone,
    )

    # Process rows
    data_vals = {}
    meta_vals = {"_fn": []}
    for li, line in enumerate(lines):
        vals, devs = process_row(
            headers,
            line.split(";"),
            datefunc,
            datecolumns,
        )
        dgutils.append_dicts(vals, devs, data_vals, meta_vals, fn, li)

    return DataTree(dgutils.dicts_to_dataset(data_vals, meta_vals, units, fulldate))
