"""
For processing of BioLogic's EC-Lab binary modular files.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.EClab_mpt

Schema
``````
The ``.mpt`` files contain many columns that vary depending on the electrochemical
technique used. Below is shown a list of columns that can be expected to be present
in a typical ``.mpt`` file.

.. code-block:: yaml

    xarray.DataTree:
      coords:
        uts:            !!float     # Unix timestamp, without date
      data_vars:
        Ewe             (uts)       # Potential of the working electrode
        Ece             (uts)       # Potential of the counter electrode, if present
        I               (uts)       # Instantaneous current
        time            (uts)       # Time elapsed since the start of the experiment
        <Ewe>           (uts)       # Average Ewe potential since last data point
        <Ece>           (uts)       # Average Ece potential since last data point
        <I>             (uts)       # Average current since last data point
        ...

.. note::

     Note that in most cases, either the instantaneous or the averaged quantities are
     stored - only rarely are both available!

Uncertainties
`````````````
- ``control_V``: VMP-3 specsheet using maximum E Range as FSR with 16-bit conversion
- ``control_I``: VMP-3 specsheet using maximum I Range as FSR with 760 µV minimum
- ``V``, ``<V>``: VMP-3 specsheet using maximum E Range as FSR
- ``I``, ``<I>``: VMP-3 specsheet using maximum I Range as FSR
- all other values: string to float conversion


Notes on file structure
```````````````````````
These human-readable files are sectioned into header lines and data lines.
The header part of the ``.mpt`` files is made up of information that can be found
in the settings, log and loop modules of the binary ``.mpr`` file.

If no header is present, the timestamps will instead be calculated from
the file's ``mtime()``.

Metadata
````````
The metadata will contain the information from the header of the file.

.. codeauthor::
    Nicolas Vetsch,
    Peter Kraus

"""

import logging
from .mpt_columns import column_units
from .techniques import param_from_key, get_unc, split_control
from babel.numbers import parse_decimal
from pathlib import Path
from typing import Any
from xarray import DataTree, Dataset, DataArray
from yadg import dgutils
from yadg.extractors import get_extract_dispatch
from yadg.dgutils.table import process_table


logger = logging.getLogger(__name__)
extract = get_extract_dispatch()


def process_settings(lines: list[str]) -> dict[str, str]:
    settings = {}
    comments = []
    for line in lines:
        items = [item.strip() for item in line.split(":")]
        if len(items) > 2:
            items = [items[0], ":".join(items[1:])]
        if len(items) == 2 and items[1] != "":
            if items[0] == "Comments":
                comments.append(items[1])
            else:
                settings[items[0]] = items[1]
    if len(comments) > 0:
        settings["Comments"] = "\n".join(comments)
    return settings


def process_params(technique: str, lines: list[str], locale: str) -> dict[str, Any]:
    params = {}
    if len(lines) == 0:
        logger.warning("No params section was found.")
        return params
    # The sequence param columns are always allocated 20 characters.
    n_sequences = int(len(lines[0]) / 20)
    prev = None
    for line in lines:
        items = [line[seq * 20 : (seq + 1) * 20].strip() for seq in range(n_sequences)]
        try:
            vals = [float(parse_decimal(val, locale=locale)) for val in items[1:]]
        except ValueError:
            vals = items[1:]
        if items[0] in {"vs."}:
            name = f"{prev} {items[0]}"
        else:
            name = items[0]
        if technique == "Battery Capacity Determination" and name == "Set I/C":
            if "Set I/C 1" in params:
                params["Set I/C 2"] = vals
            else:
                params["Set I/C 1"] = vals
        elif name not in params:
            params[name] = vals
        else:
            raise RuntimeError(f"Trying to assign same parameter {items[0]!r} twice.")
        prev = name
    return params


def process_external(lines: list[str]) -> dict:
    ret = {}
    target = ret
    for line in lines:
        k, v = line.split(":")
        k = k.strip()
        v = v.strip()
        if v == "":
            target[k] = {}
            target = target[k]
        else:
            target[k] = v
    return ret


def process_header(
    lines: list[str],
    timezone: str,
    locale: str,
) -> dict:
    """Processes the header lines.

    Parameters
    ----------
    lines
        The header lines, starting at line 3 (which is an empty line),
        right after the `"Nb header lines : "` line.

    Returns
    -------
    dict
        A dictionary containing the header contents, including settings,
        technique name, parameters, loops, and uts.

    """
    sections = "\n".join(lines).split("\n\n")
    # Can happen that no settings are present but just a loops section.
    assert not sections[1].startswith("Number of loops : "), "no settings present"
    # Again, we need the acquisition time to get timestamped data.
    assert len(sections) >= 3, "no settings present"
    technique = sections[1].strip()

    lines = sections[2].split("\n")
    pstart = None
    for li, line in enumerate(lines):
        if line.startswith("Cycle Definition :"):
            pstart = li
            break
        elif line.startswith("Ei (V)"):
            pstart = li - 1
            break

    settings = process_settings(lines[:li])
    # New thing in v11.61 - There can be an "External device configuration" section
    if li + 1 == len(lines):
        dext = 1
    elif lines[li + 1].startswith("External device configuration :"):
        li += 1
        for dext, line in enumerate(lines[li + 1 :]):
            logger.debug(f"{dext=} {line=}")
            if line.startswith(" "):
                pass
            else:
                dext += 1
                break
        settings.update(process_external(lines[li : li + dext]))
        dext += 1
    else:
        dext = 1

    params = process_params(technique, lines[pstart + dext :], locale)
    logger.critical(f"{params=}")

    for section in sections[3:]:
        if section.startswith("Modify on :"):
            extras = section.split("\n")[1:]
            for line in extras:
                if ":" in line:
                    name = line[: line.index(":")].strip()
                    val = line[line.index(":") + 1 :].strip()
                    if name in settings:
                        settings[name] = val
                        logger.info("Overwriting setting '%s' to %s.", name, val)
                        continue
                n_sequences = int(len(line) / 20)
                if n_sequences == 0:
                    continue
                items = [
                    line[seq * 20 : (seq + 1) * 20].strip()
                    for seq in range(n_sequences)
                ]
                name = items[0]
                if name in params:
                    for vi, val in enumerate(items[1:]):
                        if val == "":
                            continue
                        try:
                            val = float(parse_decimal(val, locale=locale))
                        except ValueError:
                            pass
                        params[name][vi] = val
                    logger.info("Overwriting parameter '%s' to %s.", name, params[name])

    # Parse the acquisition timestamp.
    if "Acquisition started on" in settings:
        timestamp = settings["Acquisition started on"]
        for fmt in (
            "%m/%d/%Y %H:%M:%S",
            "%m.%d.%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S.%f",
            "%m-%d-%Y %H:%M:%S",
        ):
            uts = dgutils.str_to_uts(
                timestamp=timestamp, format=fmt, timezone=timezone, strict=False
            )
            if uts is not None:
                break
        else:
            raise NotImplementedError(f"Time format for {timestamp} not implemented.")
    else:
        uts = None

    loops = None
    if len(sections) >= 4 and sections[-1].startswith("Number of loops : "):
        # The header contains a loops section.
        loops_lines = sections[-1].split("\n")
        n_loops = int(loops_lines[0].split(":")[-1])
        indexes = []
        for n in range(n_loops):
            index = loops_lines[n + 1].split("to")[0].split()[-1]
            indexes.append(int(index))
        loops = {"n_loops": n_loops, "indexes": indexes}
    ret = {
        "uts": uts,
        "technique": technique,
        "settings": settings,
        "params": params,
        "loops": loops,
    }
    return ret


def process_data(
    lines: list[str],
    locale: str,
):
    """Processes the data lines.

    Parameters
    ----------
    lines
        The data lines, starting right after the last header section.
        The first line is an empty line, the column names can be found
        on the second line.

    Returns
    -------
    dict
        A dictionary containing the datapoints in the format
        ([{column -> value}, ..., {column -> value}]). If the column
        unit is set to None, the value is an int. Otherwise, the value
        is a dict with value ("n"), sigma ("s"), and unit ("u").

    """
    # At this point the first two lines have already been read.
    # Remove extra column due to an extra tab in .mpt file column names.
    names = lines[1].split("\t")[:-1]
    units = dict()
    columns = list()
    for n in names:
        if n.strip() == "":
            continue
        c, u = column_units[n.strip()]
        if c in columns:
            logger.warning("Duplicate column '%s' with unit '%s'.", c, u)
            c = f"duplicate {c}"
        columns.append(c)
        if u is not None:
            units[c] = u
    # Remove empty lines from data_lines, see issue #151.
    data_lines = [line for line in lines[2:] if line.strip() != ""]

    if len(data_lines) > 0:
        data_vars = process_table(
            lines=data_lines,
            headers=columns,
            locale=locale,
            uncertainties_int_columns=False,
        )
    else:
        data_vars = {}

    for k in data_vars:
        if k.endswith("_uncertainty"):
            continue
        data_vars[k] = (("uts",), *data_vars[k][1:])

    if "I Range" in data_vars:
        params = [param_from_key("I Range", int(v)) for v in data_vars["I Range"][1]]
        data_vars["I Range"] = (
            data_vars["I Range"][0],
            params,
            data_vars["I Range"][2],
        )

    coords = dict()
    attrs = dict(fulldate=False)

    for k in units:
        if k in data_vars:
            data_vars[k][2]["units"] = units[k]

    ds = Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
    return ds


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    encoding: str,
    locale: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    file_magic = "EC-Lab ASCII FILE\n"
    with open(source, "r", encoding=encoding) as mpt_file:
        assert mpt_file.read(len(file_magic)) == file_magic, "invalid file magic"
        mpt = mpt_file.read()
    lines = mpt.split("\n")
    nb_header_lines = int(lines[0].split()[-1])
    header_lines = lines[: nb_header_lines - 3]
    data_lines = lines[nb_header_lines - 3 :]
    settings, params = {}, []

    if nb_header_lines <= 3:
        logger.warning("Header contains no settings and hence no timestamp.")
        start_time = 0.0
        fulldate = False
        Erange = 10.0
    else:
        header = process_header(header_lines, timezone, locale)
        start_time = header.get("uts")
        settings = header.get("settings")
        params = header.get("params")
        fulldate = True
        Er_max = params.get("E range max (V)", [10.0])
        Er_min = params.get("E range min (V)", [0.0])
        Erange = max([_max - _min for _max, _min in zip(Er_max, Er_min)])

    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params}

    # Data processing including mpt quirks
    ds = process_data(data_lines, locale)

    if "I Range" in ds:
        Irange = max(
            param_from_key("I Range", v, False) for v in set(ds["I Range"].values)
        )
    else:
        Irange = 1.0

    ds = split_control(ds)

    val, attrs = get_unc("control_V", Erange)
    ds["control_V_uncertainty"] = DataArray(val, attrs=attrs)
    val, attrs = get_unc("control_I", Irange)
    ds["control_I_uncertainty"] = DataArray(val, attrs=attrs)

    for k in {"V", "<V>", "I", "<I>"}:
        if k in ds:
            val, attrs = get_unc(k, Irange if "I" in k else Erange)
            ds[f"{k}_uncertainty"] = DataArray(val, attrs=attrs)

    if "time" in ds:
        ds["uts"] = ds["time"].values + start_time
    else:
        ds["uts"] = [start_time]
    if fulldate:
        del ds.attrs["fulldate"]
    ds.attrs["original_metadata"] = metadata
    return DataTree(ds)
