**yadg**: **y**\ et **a**\ nother **d**\ ata\ **g**\ ram
========================================================

**yadg** is a set of tools and parsers aimed to process raw instrument data. 

.. image:: images/schema_yadg_datagram.png
   :width: 600
   :alt: Diagram of the relationship between a schema, yadg, and datagram.

Given an experiment represented by a `schema`, **yadg** will process the files 
and folders specified in each experimental `step` of the `schema`, and produce a
`datagram` -- a unified data structure containing all measured ("raw") data in a 
given experiment. 

**yadg** also implements standardised processing of raw data, with features such as 
peak integration in chromatograms, quality factor determination from reflection 
coefficient traces, or simple numerical processing of tabular data.

.. toctree::
   :maxdepth: 3
   :caption: Yadg features
   :hidden:

   usage
   features
   parsers


.. toctree::
   :maxdepth: 1
   :caption: Yadg components
   :hidden:

   devdocs
   objects
   modules
