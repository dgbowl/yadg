import os
import json
import numpy as np
import tarfile
import gzip
import tempfile
import xarray as xr
from xarray import Dataset

from yadg import dgutils


def extract(
    *,
    fn: str,
    **kwargs: dict,
) -> Dataset:
    tf = tarfile.TarFile(fn, mode="r")
    with tempfile.TemporaryDirectory() as tempdir:
        tf.extractall(tempdir)

        # Get file metadata
        with open(os.path.join(tempdir, "metadata.json")) as inf:
            metadata = json.load(inf)
        uts = dgutils.str_to_uts(timestamp=metadata["startDate"], timezone=None)

        # Here we assume that "items" only has one element
        devdata = metadata["devices"]["items"][0]
        attrs = {
            "Software Version": metadata["appVersion"],
            "Model": devdata["__type"],
            "Serial": devdata["serialInternal"],
        }

        # Get necessary device metadata from the file metadata
        devices = {}
        for k, v in devdata.items():
            if isinstance(v, dict) and v["enabled"]:
                devices[k] = {
                    "id": v["channelIdentifier"],
                    "type": v["channelType"],
                    "name": v["description"],
                    "xmul": v["captureConfig"]["interval"] // 1000,
                    "npts": v["capturedSamples"],
                }

        # Get data from 1.0.gz
        with gzip.open(os.path.join(tempdir, "data-map.json.gz"), "rb") as inp:
            dmap = json.loads(inp.read())
        with gzip.open(os.path.join(tempdir, "1.0.gz"), "rb") as inp:
            raw = inp.read()

        # Convert bytes to floats
        points = {}
        for tag, params in dmap:
            _, __, namestr = tag.split(".")
            id, res, time = namestr.split("/")
            archive, start, length = params
            if id not in points:
                points[id] = np.empty(0, dtype=">f4")
            if res == "1" and archive == "1.0.gz":
                new = np.frombuffer(raw, offset=start, dtype=">f4", count=length // 4)
                points[id] = np.concatenate((points[id], new))
            elif res == "1":
                raise RuntimeError(f"Resolution of 1 but archive is {archive!r}.")

        # Push the data into the Dataset
        ds = xr.Dataset(coords={"uts": (["uts"], [])})
        for id, data in points.items():
            for k, meta in devices.items():
                if meta["id"] == id:
                    #  The type of the device should be thermocouple
                    if meta["type"] == "thermocouple":
                        unit = {"units": "degC"}
                    else:
                        raise RuntimeError("Unknown type {meta['type']!r}.")
                    yvals = data[~np.isnan(data)]
                    ydevs = np.ones(len(yvals)) * 2.2
                    xvals = np.arange(len(yvals)) * meta["xmul"] + uts
                    newds = xr.Dataset(
                        data_vars={
                            meta["name"]: (["uts"], yvals, unit),
                            f"{meta['name']}_std_err": (["uts"], ydevs, unit),
                        },
                        coords={"uts": (["uts"], xvals)},
                    )
                    ds = xr.merge((ds, newds))
        for var in ds.variables:
            if f"{var}_std_err" in ds.variables:
                ds[var].attrs["ancillary_variables"] = f"{var}_std_err"
            elif var.endswith("_std_err"):
                end = var.index("_std_err")
                if var[:end] in ds.variables:
                    ds[var].attrs["standard_name"] = f"{var[:end]} standard_error"

        ds.attrs = attrs
        return ds