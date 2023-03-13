from xarray import Dataset, DataArray
from datatree import DataTree

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
                for k, v in point.items():
                    if isinstance(v, (str, int)):
                        if k not in data:
                            data[k] = [None] * pi
                        data[k].append(v)
                    elif set(v).intersection({"n", "s", "u"}) == {"n", "s", "u"}:
                        if k not in data:
                            data[k] = [None] * pi
                        data[k].append(v["n"])
                        if k not in sigma:
                            sigma[k] = [None] * pi
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
                if k in sigma and all(sigma[k]) == sigma[k][0]:
                    attrs["sigma"] = sigma[k][0]
                elif k in sigma:
                    attrs["sigma"] = sigma[k]
                if k in units and all(units[k]) == units[k][0]:
                    attrs["units"] = units[k][0]
                da = DataArray(
                    data = v,
                    dims = ["uts"],
                    attrs = attrs
                )
                das[k] = da
            
            das["fn"] = DataArray(data = fn, dims = ["uts"])

            dt = DataTree(
                name = f"{si}", 
                data = Dataset(data_vars = das, coords = {"uts": uts}), 
                parent = root,
            )
            dt.attrs = step["metadata"]
    print(root)
    return root