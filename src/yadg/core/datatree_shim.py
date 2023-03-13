from xarray import Dataset, DataArray
from datatree import DataTree
import numpy as np


def to_datatree(dg: dict) -> DataTree:
    root = DataTree()
    root.attrs = dg["metadata"]
    for si, step in enumerate(dg["steps"]):
        if isinstance(step, DataTree):
            raise RuntimeError("DataTree step not yet implemented.")
        elif isinstance(step, Dataset):
            raise RuntimeError("Dataset step not yet implemented.")
        else:
            uts = []
            fn = []
            raw = []
            for v in step["data"]:
                uts.append(v["uts"])
                fn.append(v["fn"])
                raw.append(v["raw"])
            data = {}
            sigma = {}
            units = {}
            for pi, point in enumerate(raw):
                for k in set(data) - set(point):
                    data[k].append(np.nan)
                    if k in sigma:
                        sigma[k].append(np.nan)
                    if k in units:
                        units[k].append(None)
                for k, v in point.items():
                    if isinstance(v, (str, int)):
                        if k not in data:
                            data[k] = [None if isinstance(v, str) else np.nan] * pi
                        data[k].append(v)
                    elif set(v).intersection({"n", "s", "u"}) == {"n", "s", "u"}:
                        if k not in data:
                            data[k] = [np.nan] * pi
                        data[k].append(v["n"])
                        if k not in sigma:
                            sigma[k] = [np.nan] * pi
                        sigma[k].append(v["s"])
                        if k not in units:
                            units[k] = [None] * pi
                        if v["u"] not in {"", " ", "-", None}:
                            units[k].append(v["u"])
                        else:
                            units[k].append(None)
                    else:
                        raise RuntimeError(v.keys())
            das = {}
            for k, v in data.items():
                attrs = {}
                if k in sigma and all([s == sigma[k][0] for s in sigma[k]]):
                    attrs["sigma"] = sigma[k][0]
                elif k in sigma:
                    attrs["sigma"] = sigma[k]
                if k in units:
                    stru = [u for u in units[k] if isinstance(u, str)]
                    if len(stru) > 0 and all([u == stru[0] for u in stru]):
                        attrs["units"] = stru[0]
                    elif all([u == units[k][0] for u in units[k]]):
                        attrs["units"] = units[k][0]
                    else:
                        attrs["units"] = units[k]
                if all([f == fn[0] for f in fn]):
                    attrs["fn"] = fn[0]
                else:
                    attrs["fn"] = fn
                das[k] = DataArray(data = v, dims = ["uts"], attrs = attrs)

            dt = DataTree(
                name=f"{si}",
                data=Dataset(data_vars=das, coords={"uts": uts}),
                parent=root,
            )
            dt.attrs = step["metadata"]
    print(root)
    return root
