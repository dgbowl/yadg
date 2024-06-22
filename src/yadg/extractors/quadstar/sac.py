"""
The `sac2dat.c code from Dr. Moritz Bubek <https://www.bubek.org/sac2dat.php>`_
was a really useful stepping stone for this Python file parser.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Quadstar_sac

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      {{ trace_index }}:
        coords:
          uts:              !!float               # Unix timestamp
          mass_to_charge:   !!float               # M/Z ratio
        data_vars:
          fsr:              (None)                # Full scale range
          y:                (uts, mass_to_charge) # Signal data


Metadata
````````
The "info_position" section in the below structure is stored as metadata for every
trace, without further processing.

Notes on file structure
```````````````````````
Pretty much the entire file format has been reverse engineered. There
are still one or two unknown fields.

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

Uncertainties
`````````````
Uncertainties in ``mass_to_charge`` are set to one step in M/Z spacing.

Uncertainties in the signal ``y`` are either based on the analog-to-digital conversion
(i.e. using the full scale range), or from the upper limit of contribution of
neighboring M/Z points (50 ppm).

.. codeauthor::
    Nicolas Vetsch

"""

import numpy as np
from datatree import DataTree
import xarray as xr
import yadg.dgutils as dgutils

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
    [
        ("type", "|u1"),
        ("info_position", "<i4"),
        ("data_position", "<i4"),
    ]
)


trace_info_dtype = np.dtype(
    [
        ("data_format", "<u2"),
        ("y_title", "|S13"),
        ("y_unit", "|S13"),
        ("unknown_a", "|u1"),
        ("x_title", "|S13"),
        ("x_unit", "|S13"),
        ("comment", "|S59"),
        ("unknown_b", "|u4"),
        ("unknown_c", "|u4"),
        ("first_mass", "<f4"),
        ("scan_width", "<u2"),
        ("values_per_mass", "|u1"),
        ("zoom_start", "<f4"),
        ("zoom_end", "<f4"),
    ]
)


def _find_first_data_position(scan_headers: list[dict]) -> int:
    """Finds the data position of the first scan containing any data."""
    for header in scan_headers:
        if header["type"] != 0x11:
            continue
        return header["data_position"]


def extract(
    *,
    fn: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "rb") as sac_file:
        sac = sac_file.read()
    meta = dgutils.read_value(sac, 0x0000, general_header_dtype)
    uts_base_s = dgutils.read_value(sac, 0x00C2, "<u4")
    # The ms part of the timestamps is actually saved as tenths of ms so
    # multiplying this by 0.1 here.
    uts_base_ms = dgutils.read_value(sac, 0x00C6, "<u2") * 1e-1
    uts_base = uts_base_s + uts_base_ms * 1e-3
    trace_headers = np.frombuffer(
        sac,
        offset=0x00C8,
        dtype=trace_header_dtype,
        count=meta["n_traces"],
    )
    # Find the data position of the first data-containing timestep.
    data_pos_0 = _find_first_data_position(trace_headers)
    traces = {}
    for n in range(meta["n_timesteps"]):
        ts_offset = n * meta["timestep_length"]
        uts_offset_s = dgutils.read_value(sac, data_pos_0 - 0x0006 + ts_offset, "<u4")
        uts_offset_ms = (
            dgutils.read_value(sac, data_pos_0 - 0x0002 + ts_offset, "<u2") * 1e-1
        )
        uts_timestamp = uts_base + (uts_offset_s + uts_offset_ms * 1e-3)
        for ti, header in enumerate(trace_headers):
            if header["type"] != 0x11:
                continue
            info = dgutils.read_value(sac, header["info_position"], trace_info_dtype)
            # Construct the mass data.
            ndm = info["values_per_mass"]
            mvals, dm = np.linspace(
                info["first_mass"],
                info["first_mass"] + info["scan_width"],
                info["scan_width"] * ndm,
                endpoint=False,
                retstep=True,
            )
            mdevs = np.ones(len(mvals)) * dm
            # Read and construct the y data.
            ts_data_pos = header["data_position"] + ts_offset
            # Determine the detector's full scale range.
            fsr = 10 ** dgutils.read_value(sac, ts_data_pos + 0x0004, "<i2")
            # The n_datapoints value at timestep_data_position is
            # sometimes wrong. Calculating this here works, however.
            n_datapoints = info["scan_width"] * info["values_per_mass"]
            yvals = np.frombuffer(
                sac, offset=ts_data_pos + 0x0006, dtype="<f4", count=n_datapoints
            ).copy()
            # Once a y_value leaves the FSR it jumps to the maximum
            # of a float32. These values should be NaNs instead.
            yvals[yvals > fsr] = np.nan
            # TODO: Determine the correct accuracy from fsr. The 32bit
            # ADC is a guess that seems to put the error in the correct
            # order of magnitude.
            sigma_adc = np.ones(len(yvals)) * fsr / 2**32
            # Determine error based on contributions of neighboring masses.
            # The upper limit on contribution from peak at next integer mass is 50ppm.
            prev_neighbor = np.roll(yvals, ndm)
            prev_neighbor[:ndm] = np.nan
            next_neighbor = np.roll(yvals, -ndm)
            next_neighbor[-ndm:] = np.nan
            sigma_neighbor = np.fmax(prev_neighbor, next_neighbor) * 50e-6
            # Pick the maximum error here
            ydevs = np.fmax(sigma_adc, sigma_neighbor)
            ds = xr.Dataset(
                data_vars={
                    "fsr": fsr,
                    "mass_to_charge_std_err": (
                        ["mass_to_charge"],
                        mdevs,
                        {
                            "units": info["x_unit"],
                            "standard_name": "mass_to_charge standard_error",
                        },
                    ),
                    "y": (
                        ["uts", "mass_to_charge"],
                        [yvals],
                        {"units": info["y_unit"], "ancilliary_variables": "y_std_err"},
                    ),
                    "y_std_err": (
                        ["uts", "mass_to_charge"],
                        [ydevs],
                        {"units": info["y_unit"], "standard_name": "y standard_error"},
                    ),
                },
                coords={
                    "mass_to_charge": (
                        ["mass_to_charge"],
                        mvals,
                        {
                            "units": info["x_unit"],
                            "ancillary_variables": "mass_to_charge_std_err",
                        },
                    ),
                    "uts": (["uts"], [uts_timestamp]),
                },
                attrs=dict(original_metadata=info),
            )
            if f"{ti}" not in traces:
                traces[f"{ti}"] = ds
            else:
                try:
                    traces[f"{ti}"] = xr.concat(
                        [traces[f"{ti}"], ds], dim="uts", combine_attrs="identical"
                    )
                except xr.MergeError:
                    raise RuntimeError(
                        "Merging metadata from the individual traces has failed. "
                        "This is a bug. Please open an issue on GitHub."
                    )

    ret = DataTree.from_dict(traces)
    ret.attrs = dict(original_metadata=meta)
    return ret
