"""
For processing of BioLogic's EC-Lab binary modular files.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.EClab_mpt

Schema
``````
The ``.mpt`` files contain many columns that vary depending on the electrochemical
technique used. Below is shown a list of columns that can be expected to be present
in a typical ``.mpt`` file.

.. code-block:: yaml

    datatree.DataTree:
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

Notes on file structure
```````````````````````
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

.. codeauthor::
    Nicolas Vetsch,
    Peter Kraus

"""

import logging
from typing import Any
from babel.numbers import parse_decimal
from datatree import DataTree
from yadg import dgutils
from .techniques import get_devs, param_from_key
from .mpt_columns import column_units

logger = logging.getLogger(__name__)


def process_settings(lines: list[str]) -> dict[str, str]:
    settings = {}
    for line in lines:
        items = [item.strip() for item in line.split(":")]
        if len(items) > 2:
            items = [items[0], ":".join(items[1:])]
        if len(items) == 2 and items[1] != "":
            settings[items[0]] = items[1]
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
        if name not in params:
            params[name] = vals
        else:
            raise RuntimeError(f"Trying to assing same parameter {items[0]!r} twice.")
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
) -> tuple[dict, list, dict]:
    """Processes the header lines.

    Parameters
    ----------
    lines
        The header lines, starting at line 3 (which is an empty line),
        right after the `"Nb header lines : "` line.

    Returns
    -------
    tuple[dict, dict]
        A dictionary containing the settings (and the technique
        parameters) and a dictionary containing the loop indexes.

    """
    sections = "\n".join(lines).split("\n\n")
    # Can happen that no settings are present but just a loops section.
    assert not sections[1].startswith("Number of loops : "), "no settings present"
    # Again, we need the acquisition time to get timestamped data.
    assert len(sections) >= 3, "no settings present"
    technique = sections[1].strip()

    lines = sections[2].split("\n")
    for li, line in enumerate(lines):
        if line.startswith("Cycle Definition :"):
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
    else:
        dext = 1

    params = process_params(technique, lines[li + dext :], locale)

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
    Eranges: list[float],
    Iranges: list[float],
    controls: list[str],
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
        c, u = column_units[n.strip()]
        if c in columns:
            logger.warning("Duplicate column '%s' with unit '%s'.", c, u)
            c = f"duplicate {c}"
        columns.append(c)
        if u is not None:
            units[c] = u
    # Remove empty lines from data_lines, see issue #151.
    data_lines = [line for line in lines[2:] if line.strip() != ""]
    allvals = dict()
    allmeta = dict()
    warn_I_range = False
    for li, line in enumerate(data_lines):
        values = line.split("\t")
        vals = dict()
        devs = dict()
        for ci, name in enumerate(columns):
            value = values[ci]
            if units.get(name) is None:
                ival = int(parse_decimal(value, locale=locale))
                if name == "I Range":
                    vals[name] = param_from_key("I_range", ival)
                else:
                    vals[name] = ival
            else:
                try:
                    dec = parse_decimal(value, locale=locale)
                    vals[name] = float(dec)
                    exp = dec.as_tuple().exponent
                    devs[name] = float("nan") if isinstance(exp, str) else 10**exp
                except ValueError:
                    sval = value.strip()
                    vals[name] = sval

        Ns = vals.get("Ns", 0)
        Erange = Eranges[Ns] if isinstance(Eranges, list) else Eranges
        Irstr = Iranges[Ns] if isinstance(Iranges, list) else Iranges
        if "I Range" in vals:
            Irstr = vals["I Range"]
        Irange = param_from_key("I_range", Irstr, to_str=False)

        # I Range can be None if it's set to "Auto", "PAC" or other such string.
        if Irange is None:
            warn_I_range = True
            Irange = 1.0

        if "control_VI" in vals:
            icv = controls[Ns] if isinstance(controls, list) else controls
            name = f"control_{icv}"
            vals[name] = vals.pop("control_VI")
            units[name] = "mA" if icv in {"I", "C"} else "V"
        devs = get_devs(vals=vals, units=units, Erange=Erange, Irange=Irange, devs=devs)
        dgutils.append_dicts(vals, devs, allvals, allmeta, li=li)
    if warn_I_range:
        logger.warning("I Range could not be understood, defaulting to 1 A.")

    ds = dgutils.dicts_to_dataset(allvals, allmeta, units, fulldate=False)
    return ds


def extract(
    *,
    fn: str,
    encoding: str,
    locale: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    file_magic = "EC-Lab ASCII FILE\n"
    with open(fn, "r", encoding=encoding) as mpt_file:
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
        Eranges = 10.0
        logger.warning("E Range not specified due to missing header, setting to 10 V.")
        Iranges = "1 A"
        logger.warning("I Range not specified due to missing header, setting to 1 A.")
        controls = None
    else:
        header = process_header(header_lines, timezone, locale)
        start_time = header.get("uts")
        settings = header.get("settings")
        params = header.get("params")
        fulldate = True
        Er_max = params.get("E range max (V)", [10.0])
        Er_min = params.get("E range min (V)", [0.0])
        Eranges = [_max - _min for _max, _min in zip(Er_max, Er_min)]
        Iranges = params.get("I Range", ["1 A"])
        controls = params.get("Set I/C", params.get("Apply I/C", [None] * len(Iranges)))
    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params}

    ds = process_data(data_lines, Eranges, Iranges, controls, locale)
    if "time" in ds:
        ds["uts"] = ds["time"] + start_time
    else:
        ds["uts"] = [start_time]
    if fulldate:
        del ds.attrs["fulldate"]
    ds.attrs["original_metadata"] = metadata

    return DataTree(ds)
