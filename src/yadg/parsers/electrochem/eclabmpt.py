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
          "{{ trace_number }}":
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
import warnings
from collections import defaultdict
from datetime import datetime

from yadg.parsers.electrochem.eclabtechniques import technique_params

# Maps EC-Lab's "canonical" column names to yadg name and unit.
column_units = {
    '"Ri"/Ohm': ("'Ri'", "Ohm"),
    "-Im(Z)/Ohm": ("-Im(Z)", "Ohm"),
    "-Im(Zce)/Ohm": ("-Im(Zce)", "Ohm"),
    "-Im(Zwe-ce)/Ohm": ("-Im(Zwe-ce)", "Ohm"),
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
    "|Z|/Ohm": ("|Z|", "Ohm"),
    "|Zce|/Ohm": ("|Zce|", "Ohm"),
    "|Zwe-ce|/Ohm": ("|Zwe-ce|", "Ohm"),
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
    "R/Ohm": ("R", "Ohm"),
    "Rcmp/Ohm": ("Rcmp", "Ohm"),
    "Re(Y)/Ohm-1": ("Re(Y)", "S"),
    "Re(Y)/Ohm-1": ("Re(Y)", "S"),
    "Re(Z)/Ohm": ("Re(Z)", "Ohm"),
    "Re(Z)/Ohm": ("Re(Z)", "Ohm"),
    "Re(Zce)/Ohm": ("Re(Zce)", "Ohm"),
    "Re(Zce)/Ohm": ("Re(Zce)", "Ohm"),
    "Re(Zwe-ce)/Ohm": ("Re(Zwe-ce)", "Ohm"),
    "Re(Zwe-ce)/Ohm": ("Re(Zwe-ce)", "Ohm"),
    "step time/s": ("step time", "s"),
    "THD Ewe/%": ("THD Ewe", "%"),
    "THD I/%": ("THD I", "%"),
    "time/s": ("time", "s"),
    "x": ("x", "-"),
    "z cycle": ("z cycle", None),
}


def _process_header(lines: list[str]) -> tuple[dict, list, dict]:
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
        try:
            timestamp = datetime.strptime(timestamp, format).timestamp()
            break
        except ValueError:
            # Timestamp format does not match.
            continue
    if isinstance(timestamp, str):
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
        "posix_timestamp": timestamp,
        "technique": technique,
        "raw": "\n".join(lines),
    }
    return settings, params, loops


def _process_data(lines: list[str]) -> dict:
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
            try:
                val = float(val)
            except ValueError:
                val = val.strip()
            if unit is None:
                datapoint[col] = int(val)
            else:
                assert isinstance(val, float), "`n` should not be string"
                # TODO: Using the unit of least precision (spacing
                # between two floats) as measure of uncertainty for now.
                datapoint[col] = {
                    "n": val,
                    "s": math.ulp(val),
                    "u": unit,
                }
        datapoints.append(datapoint)
    return datapoints


def process(
    fn: str, encoding: str = "windows-1252", timezone: str = "localtime"
) -> tuple[list, dict]:
    """Processes EC-Lab human-readable text export files.

    Parameters
    ----------
    fn
        The file containing the data to parse.

    encoding
        Encoding of ``fn``, by default "windows-1252".

    timezone
        A string description of the timezone. Default is "localtime".

    Returns
    -------
    (data, metadata) : tuple[list, dict]
        Tuple containing the timesteps and metadata

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
        warnings.warn(
            "Header contains no settings and hence no timestamp. Using the file's ctime instead."
        )
        start_time = os.path.getctime(fn)
    else:
        settings, params, loops = _process_header(header_lines)
        start_time = settings.get("posix_timestamp")
    data = _process_data(data_lines)
    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params}
    timesteps = []
    # If the technique is an impedance spectroscopy, split it into
    # traces at different cycle numbers and put everything into a single
    # timestep.
    if settings.get("technique") in {"PEIS", "GEIS"}:
        # Grouping by cycle.
        cycles = defaultdict(list)
        for d in data:
            cycles[d["cycle number"]].append(d)
        # Casting cycles into traces.
        cols = data[0].keys()
        traces = {}
        for num, cycle in cycles.items():
            traces[str(num)] = {col: [d[col] for d in cycle] for col in cols}
        # Casting nominal values and sigmas into lists.
        for num, trace in traces.items():
            for key, val in trace.items():
                if not isinstance(val[0], dict):
                    continue
                trace[key] = {k: [i[k] for i in val] for k in val[0]}
                # Reducing unit list to just a string.
                trace[key]["u"] = set(trace[key]["u"]).pop()
        uts = start_time + data[0]["time"]["n"]
        timesteps = [{"uts": uts, "fn": fn, "raw": {"traces": traces}}]
        return timesteps, metadata
    # All other techniques have multiple timesteps.
    for d in data:
        uts = start_time + d["time"]["n"]
        timesteps.append({"fn": fn, "uts": uts, "raw": d})
    return timesteps, metadata
