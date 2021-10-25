import json
import numpy as np
from operator import itemgetter
from uncertainties import ufloat, umath


def combine(filelist, **kwargs):
    datagramlist = []
    for fn in filelist:
        with open(fn, "r") as infile:
            fndata = json.load(infile)
        for datagram in fndata:
            datagramlist.append(datagram)
    return datagramlist


def reduce(datagramfile, **kwargs):
    tasktype = kwargs.pop("parameters", {"type": "avg"})["type"]
    assert tasktype in [
        "avg",
        "sum",
        "diff",
    ], f'DGUTILS: reduce provided with an incorrent "type": {tasktype}.'
    with open(datagramfile, "r") as infile:
        origdg = json.load(infile)
    if tasktype == "avg":
        weights = [len(origdg) for i in range(len(origdg))]
    elif tasktype == "sum":
        weights = [1 for i in range(len(origdg))]
    elif tasktype == "diff":
        weights = [1] + [-1 for i in range(len(origdg) - 1)]
    dgzero = np.array(origdg[0]["datastream"])
    print(dgzero.shape)
    flatresult = [0.0 for i in dgzero.flatten()]
    for datagram in origdg:
        dgi = np.array(datagram["datastream"])
        assert (
            dgi.shape == dgzero.shape
        ), f"DGUTILS: reduce provided with inconsistent datagram shapes."
        weight = float(weights.pop(0))
        for i in range(len(flatresult)):
            flatresult[i] += dgi.flatten()[i] / weight
    result = {}
    result["datastream"] = np.array(flatresult).reshape(dgzero.shape).tolist()
    result["metadata"] = {}
    result["metadata"]["units"] = origdg[0]["metadata"]["units"]
    result["metadata"]["version"] = kwargs.get("ver", {})
    result["metadata"]["version"]["reduce"] = _VERSION
    return result


def printdg(datagram, **kwargs):
    print(len(datagram))


def pointdata(datagram, pars):
    results = {
        "params": {
            "cavity": {
                "r": pars["cavity"]["r"],
                "h": pars["cavity"]["h"],
                "Q": pars["cavity"]["Q"],
            },
            "sample": {
                "r": pars["sample"]["r"],
                "h": pars["sample"]["h"],
                "rho": pars["sample"]["rho"],
                "m": pars["sample"]["m"],
            },
            "mcpt": {
                "A": pars["mcpt"]["A"],
                "B": pars["mcpt"]["B"],
                "C": pars["mcpt"]["C"],
                "rp_nm": pars["mcpt"]["rp_nm"],
            },
        },
        "metadata": {
            "sample": {
                "name": pars["sample"]["name"],
                "id": pars["sample"]["id"],
                "rep": pars["sample"]["rep"],
                "date": pars["date"],
            }
        },
        "data": [],
    }

    mcptdata = [i for i in datagram if i["input"]["datagram"] == "qftrace"]
    gcdata = [i for i in datagram if i["input"]["datagram"] == "gctrace"]
    expdata = [i for i in datagram if i["input"]["datagram"] == "meascsv"]

    # MCPT parameters
    Vc = (
        np.pi
        * ufloat(*results["params"]["cavity"]["r"]) ** 2
        * ufloat(*results["params"]["cavity"]["h"])
    )
    Vs = (
        np.pi
        * ufloat(*results["params"]["sample"]["r"]) ** 2
        * ufloat(*results["params"]["sample"]["h"])
    )
    delta = (
        ufloat(*results["params"]["sample"]["m"])
        / ufloat(*results["params"]["sample"]["rho"])
    ) * (1 / Vs)
    c_i = pars["cavity"]["i"]
    s_i = pars["sample"]["i"]
    A = pars["mcpt"]["A"]
    B = pars["mcpt"]["B"]
    C = pars["mcpt"]["C"]
    timestamps = []
    for section in mcptdata:
        if pars["reference"] in section["input"]["export"]:
            Q_c = ufloat(
                np.average([p["Q0"][c_i] for p in section["results"][-10:-1]]),
                np.std([p["Q0"][c_i] for p in section["results"][-10:-1]]),
            )
        for p in section["results"]:
            timestamps.append(p["uts"])
    t0 = min(timestamps)
    tinf = max(timestamps) - t0
    Qfac = ufloat(*results["params"]["cavity"]["Q"]["TM020"]) / Q_c
    ffac = ufloat(1 / results["params"]["mcpt"]["rp_nm"], 0)

    results["params"]["cavity"]["Qfac"] = [Qfac.n, Qfac.s, "-"]
    results["params"]["cavity"]["ffac"] = [ffac.n, ffac.s, "-"]

    # inlet flow composition
    xin = []
    for section in expdata:
        xin = xin + [{"uts": p["uts"], "x": p["x"]} for p in section["results"]]
    xin = sorted(xin, key=itemgetter("uts"))

    # process one by one:
    for section in datagram:
        res = []
        if section["input"]["datagram"] == "qftrace":
            for p in section["results"]:
                f0 = p["f0"][c_i] * ffac
                Q0 = p["Q0"][c_i] * Qfac
                fs = p["f0"][s_i] * ufloat(1, 0)
                Qs = p["Q0"][s_i] * ufloat(1, 0)
                r = {
                    "uts": p["uts"],
                    "f0": [f0.n, f0.s, "Hz"],
                    "fs": [fs.n, fs.s, "Hz"],
                    "Q0": [Q0.n, Q0.s, "-"],
                    "Qs": [Qs.n, Qs.s, "-"],
                }
                s = conductivity.Qf2σ(
                    Qs, Q0, fs, f0, Vs, Vc, A=A, B=B, C=C, delta=delta
                )
                for k, v in s.items():
                    r[k] = [v.n, v.s, "S/m" if k == "σ" else "-"]
                res.append(r)
        elif section["input"]["datagram"] == "meascsv":
            for p in section["results"]:
                r = {
                    "uts": p["uts"],
                    "T": [p["T"], 0.05, "°C"],
                    "v·": [p["flow"], 0.005, "ml/min"],
                    "xin": {},
                }
                for key in p["x"]:
                    if key not in r["xin"]:
                        r["xin"][key] = [100 * p["x"][key], 0, "%"]
                tau = Vs / (ufloat(*r["v·"]) * (1e-6 / 60))
                r["τ"] = [tau.n, tau.s, "s"]
                ghsv = ufloat(*r["v·"]) * (1e-6 * 60) / Vs
                r["GHSV"] = [ghsv.n, ghsv.s, "1/h"]
                mvdot = (ufloat(*results["params"]["sample"]["m"]) * (1000)) / (
                    ufloat(*r["v·"]) / 60
                )
                r["m/v·"] = [mvdot.n, mvdot.s, "gs/ml"]
                if "C3H8" in r["xin"]:
                    phi = (ufloat(*r["xin"]["C3H8"]) / ufloat(*r["xin"]["O2"])) / (
                        1 / 5
                    )
                else:
                    phi = ufloat(0)
                r["ϕ"] = [phi.n, phi.s, "-"]
                res.append(r)
        elif section["input"]["datagram"] == "gctrace":
            for p in section["results"]:
                r = {"uts": p["uts"], "xout": {}}
                for key in [
                    "CO",
                    "methane",
                    "CO2",
                    "ethylene",
                    "ethane",
                    "propylene",
                    "propane",
                    "butane",
                    "acetic",
                    "acrylic",
                    "maleic",
                ]:
                    r["xout"][key] = [p["FID"].get(key, {}).get("x", 0), 0, "%"]
                for key in ["O2", "N2"]:
                    r["xout"][key] = [p["TCD"].get(key, {}).get("x", 0), 0, "%"]
                xC3H8 = 100 * np.interp(
                    p["uts"], [xp["uts"] for xp in xin], [xp["x"]["C3H8"] for xp in xin]
                )
                xO2 = 100 * np.interp(
                    p["uts"], [xp["uts"] for xp in xin], [xp["x"]["O2"] for xp in xin]
                )
                if xC3H8 > 1.0:
                    XS = conversion.p2XS(r["xout"], xC3H8, xO2, fuel="propane")
                    for k, v in XS.items():
                        if k.startswith("S"):
                            r[k] = {}
                            for kk, vv in v.items():
                                r[k][kk] = [vv.n, vv.s, "%"]
                        else:
                            r[k] = [v.n, v.s, "%"]
                res.append(r)
        metadata = section.get("metadata", {})
        metadata["dgutils.pointdata"] = {
            "version": _VERSION,
            "date": dateutils.now(asstr=True),
        }
        results["data"].append(
            {"input": section["input"], "metadata": metadata, "results": res}
        )
    return results
