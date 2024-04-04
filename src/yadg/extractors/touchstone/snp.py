"""
This module parses Touchstone files conforming to the Touchstone File Specification,
:ref:`revision 1.1 <https://ibis.org/connector/touchstone_spec11.pdf>`_.

.. note::

    Currently only 1- and 2-port (i.e. ``.s1p`` and ``.s2p``) files are supported.

Usage
`````
Available since ``yadg-5.1``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Touchstone_snp

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      {{ parameter_name }}                  # S11, S21, etc. for scattering parameters
        coords:
          uts:            !!float           # Unix timestamp, optional
          frequency:      !!float           #
        data_vars:
          real:           (uts, frequency)  # Real part of the response
          imag:           (uts, frequency)  # Imagunary part of the response
          magnitude:      (uts, frequency)  # Magnitude of the response
          phase_angle:    (uts, frequency)  # Phase angle of the response

Metadata
````````

Uncertainties
`````````````
Uncertainties in all variables are determined from the precision of the string-to-float
conversion.
"""

import logging
from datatree import DataTree
from xarray import Dataset, DataArray
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import numpy as np

from yadg import dgutils

logger = logging.getLogger(__name__)


def process_filename(filename: str) -> dict:
    if filename.endswith(".s1p"):
        params = ["_11"]
    elif filename.endswith(".s2p"):
        params = ["_11", "_12", "_21", "_22"]
    else:
        logger.warning("Could not determine number of ports, assuming 1 port.")
        params = ["_11"]
    return {"params": params}


def process_option(line: str) -> dict:
    _, freq_unit, param, format, _, Rref = line.split()
    if format == "DB":
        columns = ["magnitude", "phase_angle"]

        def conv(inp):
            return 20 * np.log10(np.abs(inp))
    elif format == "MA":
        columns = ["magnitude", "phase_angle"]

        def conv(inp):
            return inp
    elif format == "RI":
        columns = ["real", "imag"]
        conv = None
    else:
        raise RuntimeError(f"Unsupported format: {format!r}")

    return {
        "freq_unit": freq_unit.replace("HZ", "Hz"),
        "param": param,
        "columns": columns,
        "conv": conv,
        "Rref": float(Rref),
    }


def data_to_dataset(key: str, data: dict):
    coords = {"frequency": data["frequency"]}
    data_vars = {
        "frequency_std_err": DataArray(
            data=data["frequency_std_err"], dims=["frequency"]
        )
    }

    for k, v in data[key].items():
        data_vars[k] = DataArray(data=v, dims=coords.keys())
    return Dataset(data_vars=data_vars, coords=coords)


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, encoding=encoding) as inf:
        lines = inf.readlines()
    metadata = process_filename(fn)

    # Find options line
    for li in lines:
        if li.startswith("#"):
            metadata.update(process_option(li))
            # Only one options line is allowed - the rest is ignored, hence break
            break

    # Prepare data structures
    metadata["params"] = [p.replace("_", metadata["param"]) for p in metadata["params"]]
    cols = ["frequency"]
    data = {"frequency": [], "frequency_std_err": []}
    for k in metadata["params"]:
        data[k] = {}
        for m in metadata["columns"]:
            data[k][m] = []
            data[k][f"{m}_std_err"] = []
            cols.append((k, m))
    uts = None
    comments = []

    # Parse data lines
    for li in lines:
        if li.startswith("#"):
            continue
        elif li.startswith("!"):
            # Watch out for "! NOISE PARAMETERS"
            if "NOISE PARAMETERS" in li:
                break
            else:
                comments.append(li[1:].strip())
        else:
            # Trim comments from data lines
            if "!" in li:
                parts = li[: li.index("!")].split()
            else:
                parts = li.split()

            # For .s3p and above, we'd have to append multiple lines together here
            for k, v in zip(cols, parts):
                val, dev = tuple_fromstr(v)
                if k == "frequency":
                    data[k].append(val)
                    data[f"{k}_std_err"].append(dev)
                elif k[1] == "magnitude":
                    data[k[0]][k[1]].append(metadata["conv"](val))
                    data[k[0]][f"{k[1]}_std_err"].append(metadata["conv"](dev))
                else:
                    data[k[0]][k[1]].append(val)
                    data[k[0]][f"{k[1]}_std_err"].append(dev)

    attrs = {}
    for comment in comments:
        for fmt in ["%m/%d/%Y  %I:%M:%S %p", None]:
            # Try parsing it as timestamp
            if uts is None:
                uts = dgutils.str_to_uts(
                    timestamp=comment, timezone=timezone, format=fmt, strict=False
                )
        else:
            # Try to dig out metadata from the comment line
            for sep in [":", "="]:
                if sep in comment:
                    parts = [part.strip() for part in comment.split(sep)]
                    if len(parts) == 2:
                        attrs[parts[0]] = parts[1]
                        break
    attrs["Ref R"] = f"{metadata['Rref']} Ohm"

    dtdict = {}
    for k in metadata["params"]:
        ds = data_to_dataset(key=k, data=data)
        for var in ds.variables:
            if f"{var}_std_err" in ds.variables:
                ds[var].attrs["ancillary_variables"] = f"{var}_std_err"
            elif var.endswith("_std_err"):
                end = var.index("_std_err")
                if var[:end] in ds.variables:
                    ds[var].attrs["standard_name"] = f"{var[:end]} standard error"
            if "angle" in var:
                ds[var].attrs["units"] = "degree"
            elif "frequency" in var:
                ds[var].attrs["units"] = metadata["freq_unit"]
        if uts is not None:
            ds = ds.expand_dims(dim=dict(uts=[uts]))
        else:
            ds.attrs["fulldate"] = False
        dtdict[f"/{k}"] = ds
    dt = DataTree.from_dict(dtdict)
    dt.attrs = attrs
    return dt
