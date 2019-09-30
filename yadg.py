#!/usr/bin/env python3
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import json
import sys
import datetime
import argparse

from uncertainties import ufloat

from gctrace import *
from qftrace import *
from meascsv import *
from helpers import *
from dgutils import *
#from dbutils import *

_VERSION = "2.0"


def _inferDatagramHandler(datagramtype):
    if datagramtype == "gctrace":
        return gctrace.process
    if datagramtype == "qftrace":
        return qftrace.process
    if datagramtype == "meascsv":
        return meascsv.process
    

def _inferTodoFiles(importdict, **kwargs):
    methods = ["folders", "files", "paths"]
    assert len(set(methods) & set(importdict)) == 1, \
        f'YADG: wrong "import" method specification in importdict: {set(methods) & set(importdict)}'
    todofiles = []
    if "folders" in importdict or "files" in importdict or "paths" in importdict:
        filetype = "file"
    if "folders" in importdict:
        for folder in importdict["folders"]:
            assert os.path.exists(folder), \
                f"YADG: folder {folder} doesn't exist"
            for fn in os.listdir(folder):
                if fn.startswith(importdict.get("prefix", "")) and \
                fn.endswith(importdict.get("suffix", "")):
                    todofiles.append(os.path.join(folder, fn))
    if "files" in importdict:
        importdict["paths"] = importdict.pop("files")
    if "paths" in importdict:
        for path in importdict["paths"]:
            assert os.path.exists(path), \
                f"YADG: file {path} doesn't exist"
            todofiles.append(path)
    return sorted(todofiles), filetype

def _loadResource(resource, resourcetype, **kwargs):
    if resourcetype == "file":
        with open(resource, "r", encoding="utf8", errors='ignore') as infile:
            result = infile.readlines()
    return result

def _processSchemaFile(schemafile):
    with open(schemafile, "r") as infile:
        schemasteps = json.load(infile)
    tostore = []
    for step in schemasteps:
        data = {"input": step.copy()}
        print(f'YADG: processing step {schemasteps.index(step)} in {schemafile}:')
        assert "datagram" in step, \
            f'YADG: no "datagram" field in schema step.'
        assert "import" in step, \
            f'YADG: no "import" field in schema step.'
        assert "export" in step, \
            f'YADG: no "export" field in schema step.'
        handler = _inferDatagramHandler(step["datagram"])
        todofiles, filetype = _inferTodoFiles(step["import"])
        data["results"] = []
        for tf in todofiles:
            print(f'YADG: processing item {tf}')
            data["results"].append(handler(tf, **step.get("parameters", {})))
        tostore.append(data)
        if step["export"].lower() in ["false", "none"]:
            pass
        else:
            with open(step["export"], "w") as ofile:
                json.dump(data, ofile, indent=1)
    return(tostore)
    

parser = argparse.ArgumentParser(usage='%(prog)s [options] schemafile')
parser.add_argument('schemafile', 
                    help='schemafile to be processed by the script.')
parser.add_argument("--dump", nargs=1, 
                    help='Dump processed schemafile into a specified json file.',
                    default=False)
parser.add_argument("--version",
                    action='version', version=f'%(prog)s version {_VERSION}')
args = parser.parse_args()

if __name__ == "__main__":
    print("Processing input json: {:s}".format(args.schemafile))
    tostore = _processSchemaFile(args.schemafile)
    print(args.dump)
    if args.dump:
        with open(args.dump.pop(), "w") as ofile:
            json.dump(tostore, ofile, indent=1)
            
