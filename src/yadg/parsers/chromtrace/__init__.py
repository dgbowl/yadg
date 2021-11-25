"""
.. _parsers_chromtrace_formats:

List of supported file formats:

 - EZ-Chrom ASCII export (dat.asc) :mod:`yadg.parsers.chromtrace.ezchromasc`
 - Agilent Chemstation Chromtab (csv) :mod:`yadg.parsers.chromtrace.agilentcsv`
 - Agilent OpenLab binary signal (ch) :mod:`yadg.parsers.chromtrace.agilentch` 
 - Agilent OpenLab data archive (dx) :mod:`yadg.parsers.chromtrace.agilentdx` 
 - Fusion JSON format (json) :mod:`yadg.parsers.chromtrace.fusionjson` 
"""
from .main import process, version
