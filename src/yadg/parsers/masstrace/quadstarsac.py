"""Processing of Quadstar 32-bit scan analog data.

The [sac2dat.c code from Dr. Moritz Bubek](https://www.bubek.org/sac2dat.php)
was a really useful stepping stone for this Python adaptation.

Pretty much the entire file format has been reverse engineered. There
are still one or two unknown fields.

File Structure of `.sac` Files
``````````````````````````````

.. code-block:: python

    0x00 "data_index"
    0x02 "software_id"
    0x06 "version_major"
    0x07 "version_minor"
    0x08 "second"
    0x09 "minute"
    0x0a "hour"
    0x0b "day"
    0x0c "month"
    0x0d "year"
    0x0f "author"
    0x64 "n_timesteps"
    0x68 "n_traces"
    0x6a "timestep_length"
    ...
    # Not sure what sits from 0x6e to 0xc2.
    ...
    0xc2 "uts_base_s"
    0xc6 "uts_base_ms"
    # Trace header. Read these 9 bytes for every trace (n_traces).
    0xc8 + (n * 0x09) "type"
    0xc9 + (n * 0x09) "info_position"
    0xcd + (n * 0x09) "data_position"
    ...
    # Trace info. Read these 137 bytes for every trace where type != 0x11.
    info_position + 0x00 "data_format"
    info_position + 0x02 "y_title"
    info_position + 0x0f "y_unit"
    info_position + 0x1d "x_title"
    info_position + 0x2a "x_unit"
    info_position + 0x38 "comment"
    info_position + 0x7a "first_mass"
    info_position + 0x7e "scan_width"
    info_position + 0x80 "values_per_mass"
    info_position + 0x81 "zoom_start"
    info_position + 0x85 "zoom_end"
    ...
    # UTS offset. Read these 6 bytes for every timestep (n_timesteps).
    0xc2 + (n * timestep_length) "uts_offset_s"
    0xc6 + (n * timestep_length) "uts_offset_ms"
    # Read everything remaining below for every timestep and every trace
    # where type != 0x11.
    data_position + (n * timestep_length) + 0x00 "n_datapoints"
    data_position + (n * timestep_length) + 0x04 "data_range"
    # Datapoints. Read these 4 bytes (scan_width * values_per_mass)
    # times.
    data_position + (n * timestep_length) + 0x06 "datapoints"
    ...


Structure of Parsed Timesteps
`````````````````````````````

.. code-block:: yaml

    - fn:  !!str
    - uts: !!float
    - raw:
        traces:
          "{{ trace_number }}":  # number of the trace
            y_title:  !!str      # y-axis label from file
            comment:  !!str      # comment
            fsr:      !!str      # full scale range of detector
            m/z:                 # masses are always in amu
              {n: [!!float, ...], s: [!!float, ...], u: "amu"}
            y:                   # y-axis units from file
              {n: [!!float, ...], s: [!!float, ...], u: !!str}

.. codeauthor:: Nicolas Vetsch <vetschnicolas@gmail.com>
"""
from datetime import datetime
from typing import Any, Union

import numpy as np

# The general header at the top of .sac files.
general_header_dtype = np.dtype(
    [
        ("data_index", "<i2"),
        ("software_id", "<i4"),
        ("version_major", "|u1"),
        ("version_minor", "|u1"),
        ("S", "|u1"),
        ("M", "|u1"),
        ("H", "|u1"),
        ("d", "|u1"),
        ("m", "|u1"),
        ("y", "|u1"),
        ("username", "|S86"),
        ("n_timesteps", "<i4"),
        ("n_traces", "<i2"),
        ("timestep_length", "<i4"),
    ]
)


trace_header_dtype = np.dtype(
    [("type", "|u1"), ("info_position", "<i4"), ("data_position", "<i4"),]
)


trace_info_dtype = np.dtype(
    [
        ("data_format", "<u2"),
        ("y_title", "|S13"),
        ("y_unit", "|S14"),
        ("x_title", "|S13"),
        ("x_unit", "|S14"),
        ("comment", "|S66"),
        ("first_mass", "<f4"),
        ("scan_width", "<u2"),
        ("values_per_mass", "|u1"),
        ("zoom_start", "<f4"),
        ("zoom_end", "<f4"),
    ]
)


def _read_value(
    data: bytes, offset: int, dtype: np.dtype, encoding: str = "utf-8"
) -> Any:
    """Reads a single value from a buffer at a certain offset.

    Just a handy wrapper for np.frombuffer().

    The read value is converted to a built-in datatype using
    np.dtype.item().

    Parameters
    ----------
    data
        An object that exposes the buffer interface. Here always bytes.

    offset
        Start reading the buffer from this offset (in bytes).

    dtype
        Data-type to read in.

    encoding
        The encoding of the bytes to be converted.

    Returns
    -------
    Any
        The unpacked and converted value from the buffer.

    """
    value = np.frombuffer(data, offset=offset, dtype=dtype, count=1)
    item = value.item()
    if value.dtype.names:
        item = [i.decode(encoding) if isinstance(i, bytes) else i for i in item]
        return dict(zip(value.dtype.names, item))
    return item.decode(encoding) if isinstance(item, bytes) else item


def _read_values(
    data: bytes, offset: int, dtype: np.dtype, count: int
) -> Union[list, list[dict]]:
    """Reads in multiple values from a buffer starting at offset.

    Just a handy wrapper for np.frombuffer() with count >= 1.

    The read values are converted to a list of built-in datatypes using
    np.ndarray.tolist().

    Parameters
    ----------
    data
        An object that exposes the buffer interface. Here always bytes.

    offset
        Start reading the buffer from this offset (in bytes).

    dtype
        Data-type to read in.

    count
        Number of items to read. -1 means all data in the buffer.

    Returns
    -------
    Any
        The values read from the buffer as specified by the arguments.

    """
    values = np.frombuffer(data, offset=offset, dtype=dtype, count=count)
    if values.dtype.names:
        return [dict(zip(value.dtype.names, value.item())) for value in values]
    # The ndarray.tolist() method converts numpy scalars in ndarrays to
    # built-in python scalars. Thus not just list(values).
    return values.tolist()


def _find_first_data_position(scan_headers: list[dict]) -> int:
    """Finds the data position of the first scan containing any data."""
    for header in scan_headers:
        if header["type"] != 0x11:
            continue
        return header["data_position"]


def process(
    fn: str, encoding: str = "utf-8", timezone: str = "localtime"
) -> tuple[list, dict, None]:
    """Processes a Quadstar 32-bit analog data .sac file.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.

    """
    with open(fn, "rb") as sac_file:
        sac = sac_file.read()
    meta = _read_value(sac, 0x0000, general_header_dtype)
    uts_base_s = _read_value(sac, 0x00C2, "<u4")
    # The ms part of the timestamps is actually saved as tenths of ms so
    # multiplying this by 0.1 here.
    uts_base_ms = _read_value(sac, 0x00C6, "<u2") * 1e-1
    uts_base = uts_base_s + uts_base_ms * 1e-3
    trace_headers = _read_values(sac, 0x00C8, trace_header_dtype, meta["n_traces"])
    # Find the data position of the first data-containing timestep.
    data_pos_0 = _find_first_data_position(trace_headers)
    timesteps = []
    for n in range(meta["n_timesteps"]):
        ts_offset = n * meta["timestep_length"]
        uts_offset_s = _read_value(sac, data_pos_0 - 0x0006 + ts_offset, "<u4")
        uts_offset_ms = _read_value(sac, data_pos_0 - 0x0002 + ts_offset, "<u2") * 1e-1
        uts_timestamp = uts_base + (uts_offset_s + uts_offset_ms * 1e-3)
        traces = {}
        for trace_number, header in enumerate(trace_headers):
            if header["type"] != 0x11:
                continue
            info = _read_value(sac, header["info_position"], trace_info_dtype)
            # Construct the mass data.
            ndm = info["values_per_mass"]
            m_values, dm = np.linspace(
                info["first_mass"],
                info["first_mass"] + info["scan_width"],
                info["scan_width"] * ndm,
                endpoint=False,
                retstep=True,
            )
            m = {"n": m_values.tolist(), "s": [dm] * len(m_values), "u": info["x_unit"]}
            # Read and construct the y data.
            ts_data_pos = header["data_position"] + ts_offset
            # Determine the detector's full scale range.
            fsr = 10 ** _read_value(sac, ts_data_pos + 0x0004, "<i2")
            # The n_datapoints value at timestep_data_position is
            # sometimes wrong. Calculating this here works, however.
            n_datapoints = info["scan_width"] * info["values_per_mass"]
            y_values = _read_values(sac, ts_data_pos + 0x0006, "<f4", n_datapoints)
            # Once a y_value leaves the FSR it jumps to the maximum
            # of a float32. These values should be NaNs instead.
            y_values = [y if y <= fsr else float("NaN") for y in y_values]
            # TODO: Determine the correct accuracy from fsr. The 32bit
            # ADC is a guess that seems to put the error in the correct
            # order of magnitude.
            sigma_adc = fsr / 2 ** 32
            sigma = []
            # Contributions to neighboring masses.
            for i in range(len(y_values)):
                prev_neighbor = 0 if i < ndm else y_values[i - ndm]
                next_neighbor = 0 if i > len(y_values) - ndm - 1 else y_values[i + ndm]
                # The upper limit on contribution from peak at next
                # integer mass is 50ppm.
                sigma_neighbor = 50e-6 * max(prev_neighbor, next_neighbor)
                sigma.append(max(sigma_adc, sigma_neighbor))
            y = {
                "n": y_values,
                "s": sigma,
                "u": info["y_unit"],
            }
            traces[str(trace_number)] = {
                "y_title": info["y_title"],
                "comment": info["comment"],
                "fsr": f"{fsr:.0e}",
                "m/z": m,
                "y": y,
            }
        timesteps.append({"uts": uts_timestamp, "raw": {"traces": traces}, "fn": fn})
    version = str(meta["version_major"]) + "." + str(meta["version_minor"])
    metadata = {
        "params": {
            "software_id": meta["software_id"],
            "version": version,
            "username": meta["username"],
        }
    }
    return timesteps, metadata
