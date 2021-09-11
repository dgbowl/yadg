#!/usr/bin/env python3
import json
import argparse
import hashlib
import numpy as np
from operator import itemgetter
from uncertainties import ufloat
import matplotlib
import matplotlib.pyplot as plt


import yadg.dgutils

def main():
    parser = argparse.ArgumentParser(description="Create a png file from a datagram using params.")
    parser.add_argument("--datagram", required=True,
                        help='datagram file (processed data in json form)')
    parser.add_argument("--params", required=True,
                        help='parameter file in json form')
    parser.add_argument("--draw", default=False, action="store_true",
                        help='Draw a figure?')
    parser.add_argument("--resize", default=False, action="store_true",
                        help='Resize X axis?')
    parser.add_argument("--GSV", default=True, action="store_true", dest="volflow",
                        help='Plot flow as GSV?')
    parser.add_argument("--WF", default=False, action="store_false", dest="volflow",
                        help='Plot flow as W/F?')
    parser.add_argument("--sel", default=False, action="store_true",
                        help='Plot selectivity?')
    
    args = parser.parse_args()
    
    matplotlib.rcParams.update({
        'font.size': 12,
        'lines.markeredgewidth': 1,
        'lines.markersize': 3
    })
    
    fig = plt.figure(figsize=(8, 4.5), dpi=128)
    ax = []
    gs = fig.add_gridspec(3, 3)
    ax.append(fig.add_subplot(gs[0:2,:]))
    ax.append(ax[0].twinx())
    if args.sel:
        ax.append(ax[0].twinx())
    else:
        ax.append([])
    ax.append(fig.add_subplot(gs[2,:]))
    ax.append(ax[3].twinx())
    ax.append(ax[3].twinx())
    
    
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
    
    # split the datagram into mcpt, gc, and instrument data
    
    mcptdata = [i for i in pd["data"] if i["input"]["datagram"] == "qftrace"]
    gcdata = [i for i in pd["data"] if i["input"]["datagram"] == "gctrace"]
    expdata = [i for i in pd["data"] if i["input"]["datagram"] == "meascsv"]
    
    ax[0].set_title(f'{pars["sample"]["name"]} ({pars["sample"]["id"]}): rep. {pars["sample"]["rep"]}, {pars["date"]}')
    
    # 1 conductivity plot:
    
    # 1a calculate sigma_r using last 10 points at 225°C / 5% O2 in N2
    timestamps = []
    for section in mcptdata:
        for p in section["results"]:
            timestamps.append(p["uts"])
        if pars["reference"] in section["input"]["export"]:
            σr = ufloat(np.average([p["σ"][0] for p in section["results"][-10:-1]]),
                        np.std([p["σ"][0] for p in section["results"][-10:-1]]))
    
    # 1b determine time limits
    t0 = min(timestamps)
    tinf = max(timestamps) - t0
    
    # 1c plot MCPT data
    #    colors are either BW from section name, or provided by the user
    σmax = 100
    for section in mcptdata:
        points = section["results"]
        times = [p["uts"] - t0 for p in points]
        σ = [ufloat(*p["σ"]) for p in points]
        σ_σr = [100*(s/σr).n for s in σ]
        σmax = max(max(σ_σr),σmax)
        if "colors" in pars.get("dg2png", {}):
            color = pars["dg2png"]["colors"][mcptdata.index(section)]
        else:
            sha = hashlib.sha1()
            sha.update(section["input"]["export"][3:-5].encode())
            ha = sha.hexdigest()[:2]
            color = f"#{ha}{ha}{ha}"
        ax[0].plot([t/3600 for t in times], σ_σr, color=color, linestyle=" ", marker=".")
        ax[0].tick_params(axis="y", left=True, labelleft=True, right=False, labelright=False)
    
    ax[0].set_ylabel(r"$\frac{\sigma}{\sigma_{r}}$  [%]")
    ax[0].tick_params(axis="x", top=True, labeltop=True,  bottom=True, labelbottom=False)
    ax[0].set_xlim(left=0, right=tinf/3600)
    if args.resize:
        ax[0].set_ylim(bottom=0, top=np.ceil(σmax/50)*50)
    else:
        ax[0].set_ylim(bottom=0, top=400)
    
    # 2  flow and temperature data
    # 2a plot T and xin of propane and O2 inlet flow composition
    xin = []
    for section in expdata:
        ax[3].plot([(p["uts"] - t0) / 3600 for p in section["results"]],
                [p["T"][0] for p in section["results"]], color="k")
        ax[5].plot([(p["uts"] - t0) / 3600 for p in section["results"]],
                    [p["xin"]["C3H8"][0] for p in section["results"]], color="r")
        ax[5].plot([(p["uts"] - t0) / 3600 for p in section["results"]],
                    [p["xin"]["O2"][0] for p in section["results"]], color="b")
            
        # If we're plotting GSV:
        if args.volflow:
            ax[4].plot([(p["uts"] - t0) / 3600 for p in section["results"]],
                    [p["GHSV"][0] for p in section["results"]], color="g")
        else:
            ax[4].plot([(p["uts"] - t0) / 3600 for p in section["results"]],
                    [p["m/v·"][0] for p in section["results"]], color="g")
        xin = xin + [{"uts": p["uts"], "xin": p["xin"]} for p in section["results"]]
    xin = sorted(xin, key=itemgetter("uts"))
    # 2b temperature labels
    ax[3].set_ylim(bottom=0, top=500)
    ax[3].set_ylabel("T [°C]")
    ax[3].set_xlabel("t [h]")
    ax[3].set_xlim(ax[0].get_xlim())
    ax[3].tick_params(axis="x", top=True, labeltop=False,  bottom=True, labelbottom=True)
    
    # 2c flow labels
    if args.volflow:
        ax[4].set_ylabel(r"GHSV [s$^{-1}$]", color="g")
    else:
        ax[4].set_ylabel(r"W/F [gs/ml]", color="g")
    ax[4].tick_params(axis="y", colors="g")
    ax[4].spines.right.set_position(("axes", 1.1))
    
    ypos = np.interp(0.25*ax[0].get_xlim()[1]*3600 + t0,
                    [xp["uts"] for xp in xin], [xp["xin"]["C3H8"][0] for xp in xin])
    ax[5].annotate(r'x$_{in}$(C$_3$H$_8$) $\rightarrow$',
                    xy=(0.10*ax[0].get_xlim()[1], ypos),
                    color="r", fontsize="x-small", va="top")
    ypos = np.interp(0.25*ax[0].get_xlim()[1]*3600 + t0,
                    [xp["uts"] for xp in xin], [xp["xin"]["O2"][0] for xp in xin])
    ax[5].annotate(r'x$_{in}$(O$_2$) $\rightarrow$',
                xy=(0.10*ax[0].get_xlim()[1], ypos),
                color="b", fontsize="x-small", va="top")
    ax[5].set_ylabel(r"x$_{in}$ [%]")
    
    # 3 GC parameters
    maxX = {"t": 0, "X": 0}
    for section in gcdata:
        for p in section["results"]:
            t = p["uts"] - t0
            if p.get("Xp", [0])[0] > 0:
                ax[1].plot(t/3600, p["Xp"][0], marker="s", color="b", alpha=0.5)
                if args.sel:
                    ax[2].plot(t/3600, p["Sp"]["propylene"][0], marker=".", color="k", alpha=0.5)
                if p["Xp"][0] > maxX["X"]:
                    maxX = {"t": t/3600, "X": p["Xp"][0]}
            
    ax[1].set_ylim(bottom=0, top=np.ceil((maxX["X"]*1.10)/10)*10)
    ax[1].annotate(r'X$_p$ $\rightarrow$', xy = (maxX["t"], maxX["X"]*1.01),
                va="bottom", ha="center", fontsize="smaller", color="b")
    
    ax[1].set_ylabel("X$_p$(C$_3$H$_8$)  [%]", color="b")
    ax[1].tick_params(axis="y", colors="b")
    
    if args.sel:
        ax[2].set_ylabel("S$_p$(C$_3$H$_6$)  [%]", color="k")
        ax[2].spines.right.set_position(("axes", 1.1))
        ax[2].set_ylim(bottom = 0)
    
    plt.tight_layout(h_pad=0.0)
    if args.draw:
        plt.show()
    fig.savefig(f'plot.png', format="png", dpi=300)
