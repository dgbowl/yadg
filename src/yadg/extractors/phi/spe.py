"""
Processing of ULVAC PHI Multipak XPS traces.

The `IGOR .spe import script <https://www.wavemetrics.com/project/phispefileloader>`_ by
jjweimer was pretty helpful for writing this extractor.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Phi_spe

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      {{ trace_name }}:
        coords:
          E:            !!float               # Binding energies
        data_vars:
          y:            (E)                   # Signal data

Metadata
````````
The following metadata is extracted:

    - ``software_id``: ID of the software used to generate the file.
    - ``version``: Version of the software used to generate the file.
    - ``username``: User name used to generate the file.

Additionally, the processed header data is stored in the metadata under ``file_header``.

Notes on file structure
```````````````````````

These binary files actually contain an ASCII file header, delimited by
`"SOFH\n"` and `"EOFH\n"`.

The binding energies corresponding to the datapoints in the later part
of the file can be found from the `"SpectralRegDef"` entries in this
header. Each of these entries look something like:

.. code-block::

    2 2 F1s 9 161 -0.1250 695.0 675.0 695.0 680.0    0.160000 29.35 AREA

This maps as follows:

.. code-block::

    2           trace_number
    2           trace_number (again?)
    F1s         name
    9           atomic_number
    161         num_datapoints
    -0.1250     step
    695.0       start
    675.0       stop
    695.0       ?
    680.0       ?
    0.160000    dwell_time
    29.35       e_pass
    AREA        description (?)

After the file header, the binary part starts with a short data header
(offsets given from start of data header):

.. code-block::

    0x0000 group                # Data group number.
    0x0004 num_traces           # Number of traces in file
    0x0008 trace_header_size    # Combined lengths of all trace headers.
    0x000c data_header_size     # Length of this data header.

After this follow ``num_traces`` trace headers that are each structured
something like this:

.. code-block::

    0x0000 trace_number          # Number of the trace.
    0x0004 bool_01               # ???
    0x0008 bool_02               # ???
    0x000c trace_number_again    # Number of the trace. Again?
    0x0010 bool_03               # ???
    0x0014 num_datapoints        # Number of datapoints in trace.
    0x0018 bool_04               # ???
    0x001c bool_05               # ???
    0x0020 string_01             # ???
    0x0024 string_02             # ???
    0x0028 string_03             # ???
    0x002c int_02                # ???
    0x0030 string_04             # ???
    0x0034 string_05             # ???
    0x0038 y_unit                # The unit of the datapoints.
    0x003c int_05                # ???
    0x0040 int_06                # ???
    0x0044 int_07                # ???
    0x0048 data_dtype            # Data type for datapoints (f4 / f8).
    0x004c num_data_bytes        # Unsure about this one.
    0x0050 num_datapoints_tot    # This one as well.
    0x0054 int_10                # ???
    0x0058 int_11                # ???
    0x005c end_of_data           # Byte offset of the end-of-data.

After the trace headers follow the datapoints. After the number of
datapoints there is a single 32bit float with the trace's dwelling time
again.

Uncertainties
`````````````
The uncertainties of ``"E"`` are taken as the step-width of
the linearly spaced energy values.

The uncertainties ``"s"`` of ``"y"`` are currently set to a constant
value of ``12.5`` counts per second as all the signals in the files seen so
far only seem to take on values in those steps.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/13

    Determining the uncertainty of the counts per second signal in XPS
    traces from the phispe parser should be done in a better way.

.. codeauthor::
    Nicolas Vetsch

"""

import re
import numpy as np
import xarray as xr
import datatree
from datatree import DataTree
import yadg.dgutils as dgutils

data_header_dtype = np.dtype(
    [
        ("group", "<u4"),
        ("num_traces", "<u4"),
        ("trace_header_size", "<u4"),
        ("data_header_size", "<u4"),
    ]
)

trace_header_dtype = np.dtype(
    [
        ("trace_number", "<u4"),
        ("bool_01", "<u4"),
        ("bool_02", "<u4"),
        ("trace_number_again", "<u4"),
        ("bool_03", "<u4"),
        ("num_datapoints", "<u4"),
        ("bool_04", "<u4"),
        ("bool_05", "<u4"),
        ("string_01", "|S4"),  # pnt?
        ("string_02", "|S4"),
        ("string_03", "|S4"),  # sar?
        ("int_02", "<u4"),
        ("string_04", "|S4"),
        ("string_05", "|S4"),
        ("y_unit", "|S4"),
        ("int_05", "<u4"),
        ("int_06", "<u4"),
        ("int_07", "<u4"),
        ("data_dtype", "|S4"),
        ("num_data_bytes", "<u4"),
        ("num_datapoints_tot", "<u4"),
        ("int_10", "<u4"),
        ("int_11", "<u4"),
        ("end_of_data", "<u4"),
    ]
)


def camel_to_snake(s: str) -> str:
    """Converts CamelCase strings to snake_case.

    From https://stackoverflow.com/a/1176023

    Parameters
    ----------
    s
        The CamelCase input string.

    Returns
    -------
    str
        The snake_case equivalent of s.

    """
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def _process_header(spe: list[bytes]) -> dict:
    """Processes the file header at the top of `.spe` files.

    Parameters
    ----------
    spe
        The lines of bytes read from file.

    Returns
    -------
    dict
        The file header parsed into a dictionary. Some entries (keys)
        occur more than once. The corresponding values are joined into
        a list.

    """
    header_lines = spe[spe.index(b"SOFH\n") + 1 : spe.index(b"EOFH\n")]
    header = {}
    for line in header_lines:
        key, value = line.split(b":")
        key, value = camel_to_snake(key.decode().strip()), value.decode().strip()
        if key in header:
            header[key] = [header[key]] + [value]
        else:
            header[key] = value
    return header


def _process_trace_defs(header: dict) -> list[dict]:
    """Processes the trace definition strings given in the file header.

    These strings look something like the following:
    `2 2 F1s 9 161 -0.1250 695.0 675.0 695.0 680.0    0.160000 29.35 AREA`

    Parameters
    ----------
    header
        The file header parsed into a dictionary. The "SpectralRegDef"
        entry contains a list of trace definition strings.

    Returns
    -------
    list[dict]
        A list of trace definition dictionaries describind the kind of
        trace and the binding energy ranges.

    """
    trace_defs = []
    for trace_def in header.get("spectral_reg_def"):
        trace_def = trace_def.split()
        trace_defs.append(
            {
                "trace_number": int(trace_def[0]),
                "name": trace_def[2],
                "atomic_number": trace_def[3],
                "num_datapoints": int(trace_def[4]),
                "step": float(trace_def[5]),
                "start": float(trace_def[6]),
                "stop": float(trace_def[7]),
                "dwell_time": trace_def[10],
                "e_pass": trace_def[11],
                "description": trace_def[12],
            }
        )
    return trace_defs


def _process_traces(spe: list[bytes], trace_defs: list[dict]) -> dict:
    """Processes the spectral traces in the file.

    Parameters
    ----------
    spe
        The lines of bytes read from file.

    trace_defs
        The list of trace definitions parsed from the file header.

    Returns
    -------
    dict
        A dictionary containing the binding energies constructed from
        the trace definitions and the corrresponding XPS traces.

    """
    data = b"".join(spe[spe.index(b"EOFH\n") + 1 :])
    data_header = dgutils.read_value(data, 0x0000, data_header_dtype)
    assert data_header["num_traces"] == len(trace_defs)
    # All trace headers I have seen are 192 (0xc0) bytes long.
    assert data_header["trace_header_size"] / trace_header_dtype.itemsize == len(
        trace_defs
    )
    assert data_header["data_header_size"] == data_header_dtype.itemsize
    trace_headers = np.frombuffer(
        data,
        offset=0x0010,
        dtype=trace_header_dtype,
        count=len(trace_defs),
    )
    traces = {}
    for trace_header, trace_def in zip(trace_headers, trace_defs):
        assert trace_header["trace_number"] == trace_def["trace_number"]
        assert trace_header["num_datapoints"] == trace_def["num_datapoints"]
        # Contruct the binding energies from trace_def.
        energies, dE = np.linspace(
            trace_def["start"],
            trace_def["stop"],
            trace_def["num_datapoints"],
            endpoint=True,
            retstep=True,
        )
        # Construct data from trace_header
        data_dtype = np.dtype(f'{trace_header["data_dtype"].decode()}')
        data_offset = trace_header["end_of_data"] - trace_header["num_data_bytes"]
        datapoints = np.frombuffer(
            data,
            offset=data_offset,
            dtype=data_dtype,
            count=trace_header["num_datapoints"],
        )
        dwell_time = dgutils.read_value(data, trace_header["end_of_data"], "<f4")
        np.testing.assert_almost_equal(dwell_time, float(trace_def["dwell_time"]))
        # TODO: Figure out the correct error. This signal count should
        # somehow be a Poisson distribution, i.e. the error should be
        # something like s ~ sqrt(n). The counts per second only seem to
        # be taking values in steps of 12.5cps, so taking this as error.
        traces[str(trace_def["trace_number"])] = {
            "name": trace_def["name"],
            "atomic_number": trace_def["atomic_number"],
            "dwell_time": trace_def["dwell_time"],
            "e_pass": trace_def["e_pass"],
            "description": trace_def["description"],
            "yvals": datapoints,
            "ydevs": np.ones(len(datapoints)) * 12.5,
            "yunit": "counts / s",
            "Evals": energies,
            "Edevs": np.ones(len(energies)) * abs(dE),
            "Eunit": "eV",
        }
    return traces


def extract(
    *,
    fn: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "rb") as spe_file:
        spe = spe_file.readlines()
    header = _process_header(spe)
    software_id, version = header.get("software_version").split()
    meta = {
        "software_id": software_id,
        "version": version,
        "username": header.get("operator"),
        "file_header": header,
    }
    trace_defs = _process_trace_defs(header)
    traces = _process_traces(spe, trace_defs)
    vals = {}
    for v in traces.values():
        fvals = xr.Dataset(
            data_vars={
                "y": (
                    ["E"],
                    v["yvals"],
                    {"units": v["yunit"], "ancillary_variables": "y_std_err"},
                ),
                "y_std_err": (
                    ["E"],
                    v["ydevs"],
                    {"units": v["yunit"], "standard_name": "y standard_error"},
                ),
                "E_std_err": (
                    ["E"],
                    v["Edevs"],
                    {"units": v["Eunit"], "standard_name": "E standard_error"},
                ),
            },
            coords={
                "E": (
                    ["E"],
                    v["Evals"],
                    {"units": v["Eunit"], "ancillary_variables": "E_std_err"},
                ),
            },
        )
        vals[v["name"]] = fvals

    dt = datatree.DataTree.from_dict(vals)
    dt.attrs["original_metadata"] = meta
    return dt
