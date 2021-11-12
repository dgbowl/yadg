**yadg**: **y**\ et **a**\ nother **d**\ ata\ **g**\ ram
========================================================

**yadg** is a set of tools and parsers aimed to process raw instrument data. 

Given an experiment represented by a `schema`, **yadg** will process the files 
and folders specified in each experimental `step` of the `schema`, and produce a
`datagram` -- a unified data structure containing all measured ("raw") data in a 
given experiment. Standardised data processing of this raw data is also included,
with features such as peak integration in chromatograms, quality factor determination
from reflection coefficient traces, or simple numerical processing of tabular data.

.. include:: usage.rst

.. include:: functionality.rst

.. include:: objects.rst

.. include:: modules.rst
