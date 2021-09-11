#!/usr/bin/env python3
import json
import argparse
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline as spline
from uncertainties import ufloat, umath
from scipy import constants as const

import yadg.dgutils
import yadg.helpers
from yadg.helpers.version import _VERSION

def main():
    parser = argparse.ArgumentParser(description="Create a png file from a datagram using params.")
    parser.add_argument("--datagram", required=True,
                        help='datagram file (processed data in json form)')
    parser.add_argument("--params", required=True,
                        help='parameter file in json form')
    parser.add_argument("--preset", default="handbook",
                        help='Which protocol does the datagram correspond to?')
    parser.add_argument("--keepdata", default=False, action="store_true",
                        help='Keep individual datapoints in each section?')
    parser.add_argument("--saveas", default="dump.json",
                        help='Where to save the processed file.')
    
    args = parser.parse_args()
    
    jsdata = []
    with open(args.datagram, "r") as infile:
        dg = json.load(infile)
        if isinstance(dg, dict):
            jsdata.append(dg)
        elif isinstance(dg, list):
            jsdata += dg
    
    with open(args.params, "r") as infile:
        pars = json.load(infile)
    
    pd = yadg.dgutils.pointdata(jsdata, pars)
    results = {}
    sections = []
    fits = {}
    
    mcptdata = [i for i in pd["data"] if i["input"]["datagram"] == "qftrace"]
    gcdata = [i for i in pd["data"] if i["input"]["datagram"] == "gctrace"]
    expdata = [i for i in pd["data"] if i["input"]["datagram"] == "meascsv"]
    
    
    # calculate σr using the last 10 points at the reference conditions
    for section in mcptdata:
        if pars["reference"] in section["input"]["export"]:
            σr = ufloat(np.average([p["σ"][0] for p in section["results"][-10:-1]]),
                        np.std([p["σ"][0] for p in section["results"][-10:-1]]))
            results["σr"] = [np.average([p["σ"][0] for p in section["results"][-10:-1]]),
                            np.average([p["σ"][1] for p in section["results"][-10:-1]]),
                            "S/m"]
    
    for mcptsect in mcptdata:
        if len(mcptsect["results"]) > 80:
            l = -50
            r = -1
        else:
            l = -10
            r = -1
        sdata = {}
        # get time limits
        sdata["uts0"] = mcptsect["results"][l]["uts"]
        sdata["uts1"] = mcptsect["results"][r]["uts"]
        sdata["id"] = mcptsect["input"]["export"][0:2]
        # simple keys:
        for key in ["ε'p", "ε'b", 'ε"p', 'ε"b', "σ",
                    "T", "v·", "τ", "GHSV", "m/v·", "ϕ",
                    "Xp", "Xr", "XOr"]:
            sdata[key] = []
        # nested keys:
        for key in ["xin", "xout", "Sp", "SOp"]:
            sdata[key] = {}
        # gather points from mcptdata
        for p in mcptsect["results"][l:r]:
            for key in ["ε'p", "ε'b", 'ε"p', 'ε"b', "σ"]:
                sdata[key].append(p[key])
        # gather points from expdata and gcdata
        for expsect in expdata:
            for p in expsect["results"]:
                if p["uts"] >= sdata["uts0"] and p["uts"] <= sdata["uts1"]:
                    for key in ["T", "v·", "τ", "GHSV", "m/v·", "ϕ"]:
                        sdata[key].append(p[key])
                    for k, v in p["xin"].items():
                        if k not in sdata["xin"]:
                            sdata["xin"][k] = []
                        sdata["xin"][k].append(v)
        for gcsect in gcdata:
            for p in gcsect["results"]:
                if p["uts"] >= sdata["uts0"] and p["uts"] <= sdata["uts1"]:
                    for key in ["Xp", "Xr", "XOr"]:
                        if key in p:
                            sdata[key].append(p[key])
                    for key in ["xout", "Sp", "SOp"]:
                        if key in p:
                            for k, v in p[key].items():
                                if k not in sdata[key]:
                                    sdata[key][k] = []
                                sdata[key][k].append(v)
        # average simple keys:
        for key in ["ε'p", "ε'b", 'ε"p', 'ε"b', "σ",
                    "T", "v·", "τ", "GHSV", "m/v·", "ϕ",
                    "Xp", "Xr", "XOr"]:
            if len(sdata[key]) > 0 and len(sdata[key][0]) == 3:
                sdata[key] = [
                    np.average([i[0] for i in sdata[key]]),
                    np.std([i[0] for i in sdata[key]]),
                    sdata[key][0][2]
                ]
            if len(sdata[key]) == 0:
                del sdata[key]
        for key in ["xin", "xout", "Sp", "SOp"]:
            for k, v in sdata[key].items():
                if len(v) > 0 and len(v[0]) == 3:
                    sdata[key][k] = [
                        np.average([i[0] for i in v]),
                        np.std([i[0] for i in v]),
                        v[0][2]
                    ]
                if len(sdata[key][k]) == 0:
                    del sdata[key][k]
            if len(sdata[key]) == 0:
                del sdata[key]
        # derived variables            
        ssr = 100 * ufloat(*sdata["σ"]) / σr
        sdata["σ/σr"] = [ssr.n, ssr.s, "%"]
        if "Xp" in sdata:
            Xpm = ufloat(*sdata["Xp"]) / ufloat(*pd["params"]["sample"]["m"])
            sdata["Xp/m"] = [Xpm.n, Xpm.s, "%/kg"]
        # save
        sections.append(sdata)
    
    pd["sections"] = sections
    
    def linear(x, m, c):
        return m*x + c
    
    def polynomial(x, d, c, b, a):
        return a*x**3 + b*x**2 + c*x + d
    
    def rms(y, yfit):
        y = np.array(y)
        yfit = np.array(yfit)
        return np.sqrt(np.sum((y - yfit)**2))
    
    if args.preset == "handbook":
        tempvar = ["06", "07", "08"]
        flowvar = ["02", "03", "04", "05"]
        feedvar = ["09", "10", "11"]
        selconv = ["02", "03", "04", "05", "06"]
    elif args.preset == "perovskite":
        tempvar = ["02", "03", "04", "05", "06"]
        flowvar = ["06", "07", "08"]
        feedvar = ["09", "10"]
        selconv = ["06", "07", "08", "09"]
    elif args.preset == "oldhandbook":
        tempvar = ["07","08","09"]
        flowvar = ["03","04","05","06"]
        feedvar = ["09","10"]
        selconv = ["03","04","05","06","07"]
    
    # flow variation:
    tau = []
    sig = []
    ssr = []
    Xpm = []
    for sec in sections:
        if sec["id"] in flowvar:
            tau.append(ufloat(*sec["τ"]))
            sig.append(ufloat(*sec["σ"]))
            ssr.append(ufloat(*sec["σ/σr"]))
            Xpm.append(ufloat(*sec["Xp/m"]))
        if sec["id"] == flowvar[0]:
            ideal = ufloat(*sec["Xp/m"])/ufloat(*sec["τ"])
    if len(sig) == len(flowvar):
        for prop, tag, unit in [[ssr, "Δσ(τ)/σr", "%/s"],
                                [sig, "Δσ(τ)", "S/ms"],
                                [Xpm, "ΔX(τ)", "%/s"]]:
            popt, pcov = curve_fit(linear, [i.n for i in tau], [i.n for i in prop],
                                sigma = [i.s for i in prop], absolute_sigma = True)
            perr = np.sqrt(np.diag(pcov))
            results[tag] = [popt[0], perr[0], unit]
        Xgsv = 100 * ufloat(*results["ΔX(τ)"]) / ideal
        results["ΔX(τ)/X"] = [Xgsv.n, Xgsv.s, "%"]
        del results["ΔX(τ)"]
    
    # temp variation
    T = []
    invT = []
    lsig = []
    lXp = []
    lXpm = []
    sig = []
    for sec in sections:
        if sec["id"] in tempvar:
            try:
                T.append(ufloat(*sec["T"])+273.15)
                invT.append(1/(ufloat(*sec["T"])+273.15))
                lsig.append(umath.log(ufloat(*sec["σ"])))
                lXp.append(umath.log(ufloat(*sec["Xp"])))
                lXpm.append(umath.log(ufloat(*sec["Xp/m"])))
                sig.append(ufloat(*sec["σ"]))
            except ValueError:
                continue
    if len(sig) == len(tempvar):
        for prop, tag, unit in [[lsig, "EA(σ)", "kJ/mol"],
                                [lXp, "EA(X)", "kJ/mol"],
                                [lXpm, "EA(X/m)", "kJ/mol"]]:
            popt, pcov = curve_fit(linear, [i.n for i in invT], [i.n for i in prop],
                                sigma = [i.s for i in prop], absolute_sigma=True)
            perr = np.sqrt(np.diag(pcov))
            results[tag] = [-const.R * popt[0]/1000, const.R * perr[0]/1000, unit]
            if tag == "EA(σ)":
                RMS = rms([s.n for s in sig],
                        [np.e**(popt[1] + popt[0]/T[i].n) for i in range(len(T))])
                results[tag].append(f"RMS: {RMS:.1E} S/m")
        popt, pcov = curve_fit(linear, [i.n for i in invT],
                            [umath.log(sig[i] * T[i]).n for i in range(len(invT))],
                            sigma = [umath.log(sig[i] * T[i]).s for i in range(len(invT))],
                            absolute_sigma=True)
        perr = np.sqrt(np.diag(pcov))
        RMS = rms([s.n for s in sig],
                [np.e**(popt[1] - umath.log(T[i]) + popt[0]/T[i]).n for i in range(len(T))])
        results["EA(σT)"] = [-const.R * popt[0]/1000, const.R * perr[0]/1000, "kJ/mol",
                            f"RMS: {RMS:.1E} S/m"]
        popt, pcov = curve_fit(linear, [i.n for i in invT],
                            [umath.log(sig[i] * T[i]**(3/2)).n for i in range(len(invT))],
                            sigma = [umath.log(sig[i] * T[i]**(3/2)).s for i in range(len(invT))],
                            absolute_sigma=True)
        perr = np.sqrt(np.diag(pcov))
        RMS = rms([s.n for s in sig],
                [np.e**(popt[1] - 1.5 * umath.log(T[i]) + popt[0]/T[i]).n for i in range(len(T))])
        results["EA(σT3/2)"] = [-const.R * popt[0]/1000, const.R * perr[0]/1000, "kJ/mol",
                                f"RMS: {RMS:.1E} S/m"]
    
    # feed variation
    phi = []
    sig = []
    ssr = []
    for sec in sections:
        if sec["id"] in feedvar:
            phi.append(ufloat(*sec["ϕ"]))
            sig.append(ufloat(*sec["σ"]))
            ssr.append(ufloat(*sec["σ/σr"]))
    if len(phi) == len(feedvar):
        for prop, tag, unit in [[ssr, "Δσ(ϕ)/σr", "%"],
                                [sig, "Δσ(ϕ)", "S/m"]]:
            popt, pcov = curve_fit(linear, [i.n for i in phi], [i.n for i in prop],
                                sigma = [i.s for i in prop], absolute_sigma = True)
            perr = np.sqrt(np.diag(pcov))
            results[tag] = [popt[0], perr[0], unit]
        
    # X/S curve
    Xp = []
    SpCO = []
    SpCH = []
    for sec in sections:
        if sec["id"] in selconv:
            Xp.append(ufloat(*sec["Xp"]))
            SpCO.append(ufloat(*sec["Sp"]["CO"]) + ufloat(*sec["Sp"]["CO2"]))
            SpCH.append(ufloat(*sec["Sp"]["propylene"]))
    if len(Xp) == len(selconv):
        sort = np.argsort(Xp)
        for prop, tag, convs in [[SpCO, "SCOx", [5,10]],
                                [SpCH, "Spropylene", [5,10]]]:
            cs = spline([Xp[i].n for i in sort], [prop[i].n for i in sort],
                        w = [1/prop[i].s for i in sort], k = 2)
            csp = spline([Xp[i].n for i in sort], [prop[i].n+prop[i].s for i in sort],
                        w = [1/prop[i].s for i in sort], k = 2)
            csm = spline([Xp[i].n for i in sort], [prop[i].n-prop[i].s for i in sort],
                        w = [1/prop[i].s for i in sort], k = 2)
            for conv in convs:
                sel = float(cs(conv))
                if sel > 0 and sel < 100:
                    results[f"{tag}({conv}%)"] = [
                        sel,
                        max(abs(csp(conv)-cs(conv)), abs(csm(conv)-cs(conv))),
                        "%"
                    ]
    pd["results"] = results
    
    if not args.keepdata:
        del pd["data"]
    
    pd["metadata"].update({
        "dg2json": {
            "version": _VERSION,
            "preset": args.preset,
            "date": yadg.helpers.dateutils.now(asstr=True)
        }
    })
    
    with open(args.saveas, "w") as ofile:
        json.dump(pd, ofile, indent=1)


