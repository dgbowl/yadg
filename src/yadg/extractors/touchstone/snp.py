"""
This module parses Touchstone files conforming to the Touchstone File Specification,
`revision 1.1 <https://ibis.org/connector/touchstone_spec11.pdf>`_.

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
Metadata about the device are inferred from the structure of the comments lines, see
below. In most circumstances, the following information can be provided:

- ``Ref R``: the reference resistance (in Ohms)
- ``Model``: model number of the network analyseer
- ``Serial``: serial number of the device
- ``Software Version``: software version with which the file was created

.. note::

    The timestamp (``uts``) is also parsed from the comments in the file. In case you
    have Touchstone files with a well-defined header that is not supported by yadg,
    please open an issue.

Uncertainties
`````````````
Uncertainties in all variables are determined from the precision of the string-to-float
conversion.

Notes on file structure
```````````````````````
The Touchstone ``.sNp`` files are composed of four sections:

- options line, denoted by ``#``
- any number of comments lines, denoted by ``!``
- data lines
- a noise parameters section, delimited by ``! NOISE PARAMETERS``

Currently, only the first three sections are parsed.

.. codeauthor::
    Peter Kraus

"""

import logging
from datatree import DataTree
from xarray import Dataset, DataArray
from babel.numbers import parse_decimal

from yadg import dgutils

logger = logging.getLogger(__name__)


def process_filename(filename: str) -> dict:
    if filename.lower().endswith(".s1p"):
        params = ["_11"]
    elif filename.lower().endswith(".s2p"):
        params = ["_11", "_21", "_12", "_22"]
    else:
        logger.warning("Could not determine number of ports, assuming 1 port.")
        params = ["_11"]
    return {"params": params}


def process_options(line: str) -> dict:
    _, freq_unit, param, format, _, Rref = line.split()
    if format == "DB" or format == "dB":
        columns = ["magnitude", "phase_angle"]
        mag_unit = "dB"
    elif format == "MA":
        columns = ["magnitude", "phase_angle"]
        mag_unit = None
    elif format == "RI":
        columns = ["real", "imag"]
        mag_unit = None
    else:
        raise RuntimeError(f"Unsupported format: {format!r}")

    return {
        "freq_unit": freq_unit.replace("HZ", "Hz"),
        "param": param,
        "columns": columns,
        "mag_unit": mag_unit,
        "Rref": float(Rref),
    }


def attr_in_lines(attr: str, lines: list[str], sep: str = ":") -> dict:
    for line in lines:
        if line.startswith(attr):
            return {attr: line[line.index(sep) + 1 :].strip()}
    return {}


def process_comments(lines: list[str], tz: str) -> dict:
    attrs = {}
    uts = None
    comstr = "\n".join(lines)

    # No header - pass
    if len(lines) == 0:
        pass
    # PicoVNA 108 files
    elif "Ref Plane:" in comstr and len(lines) == 3:
        fmt = "%m/%d/%Y  %I:%M:%S %p"
        uts = dgutils.str_to_uts(
            timestamp=lines[0], timezone=tz, format=fmt, strict=False
        )
        attrs["Ref Plane"] = lines[1].split(":")[1].strip()
        attrs["Model"] = "PicoVNA 108"
    # Agilent N523* and E50* export
    elif "Agilent Technologies" in lines[0] or "Keysight Technologies" in lines[0]:
        _, model, serial, version = lines[0].split(",")
        attrs["Model"] = model
        attrs["Serial"] = serial
        attrs["Software Version"] = version
        attrs.update(attr_in_lines("Correction", lines, ":"))
        datestr = attr_in_lines("Date", lines, ":")["Date"]
        for fmt in ["%A, %B %d, %Y %H:%M:%S", "%a %b %d %H:%M:%S %Y"]:
            uts = dgutils.str_to_uts(
                timestamp=datestr, timezone=tz, format=fmt, strict=False
            )
            if uts is not None:
                break
    # Agilent N991* export
    elif "Agilent N99" in lines[0] or "Keysight N99" in lines[0]:
        attrs.update(attr_in_lines("Model", lines, ":"))
        attrs.update(attr_in_lines("Serial", lines, ":"))
        datestr = attr_in_lines("Date", lines, ":")["Date"]
        fmt = "%A, %d %B %Y %H:%M:%S"
        uts = dgutils.str_to_uts(
            timestamp=datestr, timezone=tz, format=fmt, strict=False
        )
    # Rohde & Schwarz ZVA/ZVB export
    elif "Rohde & Schwarz" in lines[0]:
        model, version, serial = lines[0].split(" - ")
        attrs["Model"] = model
        attrs["Serial"] = serial
        attrs["Software Version"] = version
        datestr = attr_in_lines("Date", lines, ":")["Date"]
        fmt = "%Y-%m-%d %H:%M:%S"
        uts = dgutils.str_to_uts(
            timestamp=datestr, timezone=tz, format=fmt, strict=False
        )
    # Unknown header - pass
    else:
        pass
    return uts, attrs


def data_to_dataset(key: str, data: dict) -> Dataset:
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
    locale: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, encoding=encoding) as inf:
        lines = inf.readlines()
    metadata = process_filename(fn)

    # Find options line
    for li in lines:
        if li.startswith("#"):
            metadata.update(process_options(li))
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
                dec = parse_decimal(v, locale=locale)
                exp = dec.as_tuple().exponent
                val = float(dec)
                dev = 10**exp
                if k == "frequency":
                    data[k].append(val)
                    data[f"{k}_std_err"].append(dev)
                elif k[1] == "magnitude":
                    data[k[0]][k[1]].append(val)
                    data[k[0]][f"{k[1]}_std_err"].append(dev)
                else:
                    data[k[0]][k[1]].append(val)
                    data[k[0]][f"{k[1]}_std_err"].append(dev)

    uts, attrs = process_comments(comments, timezone)
    attrs["Ref R"] = f"{metadata['Rref']} Ohm"

    dtdict = {"/": Dataset(attrs=dict(original_metadata=attrs))}
    for k in metadata["params"]:
        ds = data_to_dataset(key=k, data=data)
        for var in ds.variables:
            if f"{var}_std_err" in ds.variables:
                ds[var].attrs["ancillary_variables"] = f"{var}_std_err"
            elif var.endswith("_std_err"):
                end = var.index("_std_err")
                if var[:end] in ds.variables:
                    ds[var].attrs["standard_name"] = f"{var[:end]} standard_error"
            if "angle" in var:
                ds[var].attrs["units"] = "degree"
            elif "frequency" in var:
                ds[var].attrs["units"] = metadata["freq_unit"]
            elif "magnitude" in var and metadata["mag_unit"] is not None:
                ds[var].attrs["units"] = metadata["mag_unit"]
        if uts is not None:
            ds = ds.expand_dims(dim=dict(uts=[uts]))
        else:
            ds.attrs["fulldate"] = False
        dtdict[f"/{k}"] = ds
    dt = DataTree.from_dict(dtdict)
    return dt
