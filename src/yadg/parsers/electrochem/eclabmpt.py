"""Processing of BioLogic's EC-Lab ASCII export files.

File Structure of `.mpt` Files
``````````````````````````````

These human-readable files are sectioned into headerlines and datalines.
The header part at is made up of information that can be found in the
settings, log and loop modules of the binary `.mpr` file.

If no header is present, the timestamps will instead be calculated from
the file's ctime.


Structure of Parsed Data
````````````````````````

*EIS Techniques (PEIS/GEIS)*

.. code-block:: yaml

    - fn   !!str
    - uts  !!float
    - raw:
        traces:
          "{{ technique name }}":
            "{{ col1 }}":
              [!!int, ...]
            "{{ col2 }}":
              {n: [!!float, ...], s: [!!float, ...], u: !!str}

*All Other Techniques*

.. code-block:: yaml

    - fn   !!str
    - uts  !!float
    - raw:
        "{{ col1 }}":  !!int
        "{{ col2 }}":
          {n: !!float, s: !!float, u: !!str}

.. codeauthor:: Nicolas Vetsch <vetschnicolas@gmail.com>
"""
import math
import os
import re
import logging
from collections import defaultdict
from yadg.dgutils.dateutils import str_to_uts

from yadg.parsers.electrochem.eclabtechniques import (
    get_resolution,
    technique_params,
    param_from_key,
)

# Maps EC-Lab's "canonical" column names to yadg name and unit.
column_units = {
    '"Ri"/Ohm': ("'Ri'", "Ω"),
    "-Im(Z)/Ohm": ("-Im(Z)", "Ω"),
    "-Im(Zce)/Ohm": ("-Im(Zce)", "Ω"),
    "-Im(Zwe-ce)/Ohm": ("-Im(Zwe-ce)", "Ω"),
    "(Q-Qo)/C": ("(Q-Qo)", "C"),
    "(Q-Qo)/mA.h": ("(Q-Qo)", "mA·h"),
    "<Ece>/V": ("<Ece>", "V"),
    "<Ewe>/V": ("<Ewe>", "V"),
    "<I>/mA": ("<I>", "mA"),
    "|Ece|/V": ("|Ece|", "V"),
    "|Energy|/W.h": ("|Energy|", "W·h"),
    "|Ewe|/V": ("|Ewe|", "V"),
    "|I|/A": ("|I|", "A"),
    "|Y|/Ohm-1": ("|Y|", "S"),
    "|Z|/Ohm": ("|Z|", "Ω"),
    "|Zce|/Ohm": ("|Zce|", "Ω"),
    "|Zwe-ce|/Ohm": ("|Zwe-ce|", "Ω"),
    "Analog IN 1/V": ("Analog IN 1", "V"),
    "Analog IN 2/V": ("Analog IN 2", "V"),
    "Capacitance charge/µF": ("Capacitance charge", "µF"),
    "Capacitance discharge/µF": ("Capacitance discharge", "µF"),
    "Capacity/mA.h": ("Capacity", "mA·h"),
    "charge time/s": ("charge time", "s"),
    "Conductivity/S.cm-1": ("Conductivity", "S/cm"),
    "control changes": ("control changes", None),
    "control/mA": ("control_I", "mA"),
    "control/V": ("control_V", "V"),
    "control/V/mA": ("control_V/I", "V/mA"),
    "counter inc.": ("counter inc.", None),
    "Cp-2/µF-2": ("Cp⁻²", "µF⁻²"),
    "Cp/µF": ("Cp", "µF"),
    "Cs-2/µF-2": ("Cs⁻²", "µF⁻²"),
    "Cs/µF": ("Cs", "µF"),
    "cycle number": ("cycle number", None),
    "cycle time/s": ("cycle time", "s"),
    "d(Q-Qo)/dE/mA.h/V": ("d(Q-Qo)/dE", "mA·h/V"),
    "dI/dt/mA/s": ("dI/dt", "mA/s"),
    "discharge time/s": ("discharge time", "s"),
    "dQ/C": ("dQ", "C"),
    "dq/mA.h": ("dq", "mA·h"),
    "dQ/mA.h": ("dQ", "mA·h"),
    "Ece/V": ("Ece", "V"),
    "Ecell/V": ("Ecell", "V"),
    "Efficiency/%": ("Efficiency", "%"),
    "Energy charge/W.h": ("Energy charge", "W·h"),
    "Energy discharge/W.h": ("Energy discharge", "W·h"),
    "Energy/W.h": ("Energy", "W·h"),
    "error": ("error", None),
    "Ewe-Ece/V": ("Ewe-Ece", "V"),
    "Ewe/V": ("Ewe", "V"),
    "freq/Hz": ("freq", "Hz"),
    "half cycle": ("half cycle", None),
    "I Range": ("I Range", None),
    "I/mA": ("I", "mA"),
    "Im(Y)/Ohm-1": ("Im(Y)", "S"),
    "mode": ("mode", None),
    "Ns changes": ("Ns changes", None),
    "Ns": ("Ns", None),
    "NSD Ewe/%": ("NSD Ewe", "%"),
    "NSD I/%": ("NSD I", "%"),
    "NSR Ewe/%": ("NSR Ewe", "%"),
    "NSR I/%": ("NSR I", "%"),
    "ox/red": ("ox/red", None),
    "P/W": ("P", "W"),
    "Phase(Y)/deg": ("Phase(Y)", "deg"),
    "Phase(Z)/deg": ("Phase(Z)", "deg"),
    "Phase(Zce)/deg": ("Phase(Zce)", "deg"),
    "Phase(Zwe-ce)/deg": ("Phase(Zwe-ce)", "deg"),
    "Q charge/discharge/mA.h": ("Q charge/discharge", "mA·h"),
    "Q charge/mA.h": ("Q charge", "mA·h"),
    "Q charge/mA.h/g": ("Q charge", "mA·h/g"),
    "Q discharge/mA.h": ("Q discharge", "mA·h"),
    "Q discharge/mA.h/g": ("Q discharge", "mA·h/g"),
    "R/Ohm": ("R", "Ω"),
    "Rcmp/Ohm": ("Rcmp", "Ω"),
    "Re(Y)/Ohm-1": ("Re(Y)", "S"),
    "Re(Y)/Ohm-1": ("Re(Y)", "S"),
    "Re(Z)/Ohm": ("Re(Z)", "Ω"),
    "Re(Z)/Ohm": ("Re(Z)", "Ω"),
    "Re(Zce)/Ohm": ("Re(Zce)", "Ω"),
    "Re(Zce)/Ohm": ("Re(Zce)", "Ω"),
    "Re(Zwe-ce)/Ohm": ("Re(Zwe-ce)", "Ω"),
    "Re(Zwe-ce)/Ohm": ("Re(Zwe-ce)", "Ω"),
    "step time/s": ("step time", "s"),
    "THD Ewe/%": ("THD Ewe", "%"),
    "THD I/%": ("THD I", "%"),
    "time/s": ("time", "s"),
    "x": ("x", " "),
    "z cycle": ("z cycle", None),
}


def _process_header(lines: list[str], timezone: str) -> tuple[dict, list, dict]:
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
    # The sequence param columns are always allocated 20 characters.
    n_sequences = int(len(params[0]) / 20)
    params_values = []
    for seq in range(1, n_sequences):
        values = []
        for param in params:
            try:
                val = float(param[seq * 20 : (seq + 1) * 20])
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
        uts = str_to_uts(timestamp, format, timezone, False)
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
        "raw": "\n".join(lines),
    }
    return settings, params, loops


def _process_data(lines: list[str], Eranges: list[float], Iranges: list[float]) -> dict:
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
    columns, units = zip(*[column_units[n] for n in names])
    data_lines = lines[2:]
    datapoints = []
    for line in data_lines:
        values = line.split("\t")
        datapoint = {}
        for col, val, unit in list(zip(columns, values, units)):
            if unit is None:
                ival = int(float(val))
                if col == "I Range":
                    datapoint[col] = param_from_key("I_range", ival)
                    Irange = param_from_key("I_range", ival, to_str=False)
                else:
                    datapoint[col] = ival
        if "Ns" in datapoint:
            Erange = Eranges[datapoint["Ns"]]
        else:
            logging.info(
                "eclab.mpr: 'Ns' is not in data table, "
                "using the first E range specified in params."
            )
            Erange = Eranges[0]
        if "I Range" not in datapoint:
            logging.info(
                "eclab.mpr: 'I Range' is not in data table, "
                "using the I range specified in params."
            )
            if "Ns" in datapoint:
                Irstr = Iranges[datapoint["Ns"]]
            else:
                Irstr = Iranges[0]
            Irange = param_from_key("I_range", Irstr, to_str=False)
        for col, val, unit in list(zip(columns, values, units)):
            try:
                val = float(val)
            except ValueError:
                val = val.strip()
            if unit is None:
                continue
            assert isinstance(val, float), "`n` should not be string"
            s = get_resolution(col, val, Erange, Irange)
            datapoint[col] = {"n": val, "s": s, "u": unit}
        datapoints.append(datapoint)
    return datapoints


def process(
    fn: str, encoding: str = "windows-1252", timezone: str = "UTC"
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
    settings, params, loops = {}, [], {}
    if nb_header_lines <= 3:
        logging.warning("eclabmpt: Header contains no settings and hence no timestamp.")
        start_time = 0.0
        fulldate = False
        Eranges = [20.0]
        Iranges = ["Auto"]
    else:
        settings, params, loops = _process_header(header_lines, timezone)
        start_time = settings.get("posix_timestamp")
        fulldate = True
        Eranges = []
        Iranges = []
        for el in params:
            Eranges.append(el["E_range_max"] - el["E_range_min"])
            Iranges.append(el.get("I_range", "Auto"))
    data = _process_data(data_lines, Eranges, Iranges)
    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params}
    timesteps = []
    # If the technique is an impedance spectroscopy, split it into
    # traces at different cycle numbers and put each trace into its own timestep
    if settings["technique"] in {"PEIS", "GEIS"}:
        # Grouping by cycle.
        cycles = defaultdict(list)
        for d in data:
            cycles[d["cycle number"]].append(d)
        # Casting cycles into traces.
        for ti, td in cycles.items():
            trace = {col: [d[col] for d in td] for col in td[0].keys()}
            for key, val in trace.items():
                if not isinstance(val[0], dict):
                    continue
                trace[key] = {k: [i[k] for i in val] for k in val[0]}
                # Reducing unit list to just a string.
                trace[key]["u"] = set(trace[key]["u"]).pop()
            uts = start_time + trace["time"]["n"][0]
            trace["time"]["n"] = [i - trace["time"]["n"][0] for i in trace["time"]["n"]]
            timesteps.append(
                {
                    "uts": uts,
                    "fn": fn,
                    "raw": {"traces": {settings["technique"]: trace}},
                }
            )
        return timesteps, metadata, fulldate
    # All other techniques have multiple timesteps.
    for d in data:
        uts = start_time + d["time"]["n"]
        timesteps.append({"fn": fn, "uts": uts, "raw": d})
    return timesteps, metadata, fulldate
