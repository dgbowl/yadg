import re
import logging
import locale
import pandas as pd
from collections import defaultdict
from ...dgutils.dateutils import str_to_uts
from ..eclabcommon.techniques import get_resolution, technique_params, param_from_key

logger = logging.getLogger(__name__)

from .mpt_columns import column_units


def process_header(lines: list[str], timezone: str) -> tuple[dict, list, dict]:
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
    settings_lines = sections[2].split("\n")
    technique, params_keys = technique_params(technique, settings_lines)
    params = settings_lines[-len(params_keys) :]

    # Get the locale
    old_loc = locale.getlocale(category=locale.LC_NUMERIC)
    ewe_ctrl_re = re.compile(r"Ewe ctrl range : min = (?P<min>.+), max = (?P<max>.+)")
    ewe_ctrl_match = ewe_ctrl_re.search("\n".join(settings_lines))
    for loc in [old_loc, "de_DE.UTF-8", "en_GB.UTF-8", "en_US.UTF-8"]:
        try:
            locale.setlocale(locale.LC_NUMERIC, locale=loc)
            locale.atof(ewe_ctrl_match["min"].split()[0])
            locale.atof(ewe_ctrl_match["max"].split()[0])
            logging.debug(f"The locale of the current file is '{loc}'.")
            break
        except ValueError:
            logging.debug(f"Could not parse Ewe ctrl using locale '{loc}'.")

    # The sequence param columns are always allocated 20 characters.
    n_sequences = int(len(params[0]) / 20)
    params_values = []
    for seq in range(1, n_sequences):
        values = []
        for param in params:
            try:
                val = locale.atof(param[seq * 20 : (seq + 1) * 20])
            except ValueError:
                val = param[seq * 20 : (seq + 1) * 20].strip()
            values.append(val)
        params_values.append(values)
    params = [dict(zip(params_keys, values)) for values in params_values]
    settings_lines = [line.strip() for line in settings_lines[: -len(params_keys)]]

    # Parse the acquisition timestamp.
    timestamp_re = re.compile(r"Acquisition started on : (?P<val>.+)")
    timestamp_match = timestamp_re.search("\n".join(settings_lines))
    timestamp = timestamp_match["val"]
    for format in ("%m/%d/%Y %H:%M:%S", "%m.%d.%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S.%f"):
        uts = str_to_uts(
            timestamp=timestamp, format=format, timezone=timezone, strict=False
        )
        if uts is not None:
            break
    if uts is None:
        raise NotImplementedError(f"Time format for {timestamp} not implemented.")

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
    settings = {
        "posix_timestamp": uts,
        "technique": technique,
    }
    return settings, params, loops


def process_data(
        lines: list[str], 
        Eranges: list[float], 
        Iranges: list[float]
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
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
        c, u = column_units[n]
        columns.append(c)
        if u is not None:
            units[c] = u
    data_lines = lines[2:]
    records = {"nominal": [], "sigma": []}
    for line in data_lines:
        values = line.split("\t")
        for vi, val in enumerate(values):
            if units.get(columns[vi]) is None:
                ival = int(locale.atof(val))
                if columns[vi] == "I Range":
                    values[vi] = param_from_key("I_range", ival)
                else:
                    values[vi] = ival
            else:
                try:
                    fval = locale.atof(val)
                    values[vi] = fval
                except ValueError:
                    sval = val.strip()
                    values[vi] = sval
        records["nominal"].append(values)

        if "Ns" in columns:
            val = values[columns.index("Ns")]
            Erange = Eranges[val]
            Irstr = Iranges[val]
        else:
            Erange = Eranges[0]
            Irstr = Iranges[0]
        if "I Range" in columns:
            Irstr = values[columns.index("I Range")]
        Irange = param_from_key("I_range", Irstr, to_str=False)
        
        sigmas = {}
        for col, val in list(zip(columns, values)):
            unit = units.get(col)
            if unit is None:
                continue
            assert isinstance(val, float), "`n` should not be string"
            sigmas[col] = get_resolution(col, val, unit, Erange, Irange)
        records["sigma"].append(sigmas)
    
    nominal = pd.DataFrame.from_records(records["nominal"], columns=columns)
    sigma = pd.DataFrame.from_records(records["sigma"])

    return nominal, sigma, units


def process(
    fn: str,
    encoding: str = "windows-1252",
    timezone: str = "UTC",
) -> tuple[list, dict, bool]:
    """Processes EC-Lab human-readable text export files.

    Parameters
    ----------
    fn
        The file containing the data to parse.

    encoding
        Encoding of ``fn``, by default "windows-1252".

    timezone
        A string description of the timezone. Default is "UTC".

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and the full date tag. For mpt files,
        the full date might not be specified if header is not present.

    """
    file_magic = "EC-Lab ASCII FILE\n"
    with open(fn, "r", encoding=encoding) as mpt_file:
        assert mpt_file.read(len(file_magic)) == file_magic, "invalid file magic"
        mpt = mpt_file.read()
    lines = mpt.split("\n")
    nb_header_lines = int(lines[0].split()[-1])
    header_lines = lines[: nb_header_lines - 3]
    data_lines = lines[nb_header_lines - 3 :]
    settings, params = {}, []
    
    # Store current LC_NUMERIC before we do anything:
    old_loc = locale.getlocale(category=locale.LC_NUMERIC)
    if nb_header_lines <= 3:
        logger.warning("Header contains no settings and hence no timestamp.")
        start_time = 0.0
        fulldate = False
        Eranges = [20.0]
        Iranges = ["Auto"]
    else:
        settings, params, _ = process_header(header_lines, timezone)
        start_time = settings.get("posix_timestamp")
        fulldate = True
        Eranges = []
        Iranges = []
        for el in params:
            E_range_max = el.get("E_range_max", float("inf"))
            E_range_min = el.get("E_range_min", float("-inf"))
            Eranges.append(E_range_max - E_range_min)
            Iranges.append(el.get("I_range", "Auto"))
    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params, "fulldate": fulldate}

    nominal, sigma, units = process_data(data_lines, Eranges, Iranges)
    if fulldate:
        nominal["uts"] = nominal["time"] + start_time
        sigma["uts"] = nominal["uts"]
        nominal.set_index("uts", inplace=True)
        sigma.set_index("uts", inplace=True)

    # reset to original LC_NUMERIC
    locale.setlocale(category=locale.LC_NUMERIC, locale=old_loc)
    return metadata, nominal, sigma, units
