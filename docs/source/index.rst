**yadg**: yet another datagram
==============================

yadg is a set of tools and parsers aimed to process raw instrument data.

.. image:: images/schema_yadg_datagram.png
   :width: 600
   :alt: yadg is used to process raw data files using a DataSchema into a datagram.

Given an experiment represented by a `dataschema`, yadg will process the files 
and folders specified in each experimental `step` of the `dataschema`, and produce a
`datagram` -- a unified data structure containing all measured ("raw") data in a 
given experiment. 

The produced `datagram` is associated with full provenance info, and the data within
the `datagram` contains instrumental error estimates and is annotated with units.

yadg also contains some tools for a standardised processing of raw data, including
features such as peak integration in chromatograms, quality factor determination 
from reflection coefficient traces, applying calibration curves to data, or simple
numerical processing of tabular data. The "derived" data obtained this way is
systematically separated from the "raw" data.

.. toctree::
   :maxdepth: 3
   :caption: yadg user manual
   :hidden:

   usage
   features
   parsers
   citing


.. toctree::
   :maxdepth: 1
   :caption: yadg developer manual
   :hidden:

   devdocs
   version
   objects
   yadg
