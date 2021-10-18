import logging
import json
from striprtf.striprtf import rtf_to_text

from yadg.parsers.basiccsv import process_row
from yadg.dgutils.dateutils import infer_timestamp_from, date_from_str

def drycal_rtf(fn: str, encoding: str, date: float, 
               calib: dict) -> tuple[list, dict, None]:
    with open(fn, "r", encoding = encoding) as infile:
        rtf = infile.read()
    lines = rtf_to_text(rtf).split("\n")
    for li in range(len(lines)):
        if lines[li].startswith("Sample"):
            si = li
        elif lines[li].startswith("1|"):
            di = li
            break
    # Metadata processing for rtf files is in columns, not rows.
    ml = []
    metadata = dict()
    for line in lines[:si]:
        if line.strip() != "":
            items = [i.strip() for i in line.split("|")]
            if len(items) > 1:
                ml.append(items)
    assert len(ml) == 2 and len(ml[0]) == len(ml[1])
    for i in range(len(ml[0])):
        if ml[0][i] != "":
            metadata[ml[0][i]] = ml[1][i]
    
    # Process data table
    dl = []
    dl.append(" ".join(lines[si:di]))
    for line in lines[di:]:
        if line.strip() != "":
            dl.append(line)
    headers, units, data = drycal_table(dl, sep = "|")
    datecolumns, datefunc = infer_timestamp_from([], {
        "time": {"index": 4, "format": "%I:%M:%S %p"}
    })
    
    # Correct each ts by provided date
    timesteps = []
    for row in data:
        ts = process_row(headers[1:], row[1:], units, datefunc, 
                         datecolumns, calib = calib)
        ts["uts"] += date
        ts["fn"] = fn
        timesteps.append(ts)
    
    return timesteps, metadata, None

def drycal_sep(fn: str, encoding: str, date: float, 
               calib: dict, sep: str) -> tuple[list, dict, None]:
    with open(fn, "r") as infile:
        lines = infile.readlines()
    for li in range(len(lines)):
        if lines[li].startswith("Sample"):
            si = li
        elif lines[li].startswith(f"1{sep}"):
            di = li
            break
    # Metadata processing for csv files is standard.
    ml = []
    metadata = dict()
    for line in lines[:si]:
        if line.strip() != "":
            items = [i.strip() for i in line.split(sep)]
            if len(items) == 2:
                metadata[items[0]] = items[1]
    
    # Process data table
    dl = []
    dl.append(" ".join(lines[si:di]))
    for line in lines[di:]:
        if line.strip() != "":
            dl.append(line)
    headers, units, data = drycal_table(dl, sep = sep)
    datecolumns, datefunc = infer_timestamp_from([], {
        "time": {"index": 4, "format": "%H:%M:%S"}
    })
    
    # Correct each ts by provided date
    timesteps = []
    for row in data:
        ts = process_row(headers[1:], row[1:], units, datefunc, 
                         datecolumns, calib = calib)
        ts["uts"] += date
        ts["fn"] = str(fn)
        timesteps.append(ts)
    
    return timesteps, metadata, None

def drycal_table(lines: list, sep: str = ",") -> tuple[list, dict, list]:
    items = [i.strip() for i in lines[0].split(sep)]
    headers = []
    units = {}
    data = []
    for item in items:
        for rs in [". ", " "]:
            parts = item.split(rs)
            if len(parts) == 2:
                break
        headers.append(parts[0])
        if len(parts) == 2:
            units[parts[0]] = parts[1]
        else:
            units[parts[0]] = "-"
    if items[-1] == "":
        trim = True
        headers = headers[:-1]
    for line in lines[1:]:
        cols = line.split(sep)
        assert len(cols) == len(items)
        if trim:
            data.append(cols[:-1])
        else:
            data.append(cols)
    return headers, units, data

def process(fn: str, encoding: str = "utf-8", filetype: str = None, 
            atol: float = 0.0, rtol: float = 0.0, sigma: dict = {}, 
            convert: dict = None, calfile: str = None, 
            date: str = None, **kwargs) -> tuple[list, dict, dict]:
    """
    DryCal log file processor.
    
    """
    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if convert is not None:
        calib.update(convert)
    
    if date is None:
        date = fn
    date = date_from_str(date)
    assert date is not None, "Log starting date must be specified."
    
    metadata = {"fn": str(fn)}

    if filetype == "rtf" or (filetype is None and fn.endswith("rtf")):
        ts, meta, comm = drycal_rtf(fn, encoding, date, calib)
    elif filetype == "csv" or (filetype is None and fn.endswith("csv")):
        ts, meta, comm = drycal_sep(fn, encoding, date, calib, ",")
    elif filetype == "txt" or (filetype is None and fn.endswith("txt")):
        ts, meta, comm = drycal_sep(fn, encoding, date, calib, "\t")
    
    metadata.update(meta)

    return ts, metadata, comm
