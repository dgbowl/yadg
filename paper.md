---
title: 'yadg: Yet another datagram'
tags:
  - Python
  - chemistry
  - catalysis
  - electrochemistry
  - FAIR data
authors:
  - name: Peter Kraus^[corresponding author] 
    orcid: 0000-0002-4359-5003
    affiliation: 1 
  - name: Nicolas Vetsch
    affiliation: 1
  - name: Corsin Battaglia
    affiliation: 1
affiliations:
 - name: |
      Empa - Swiss Federal Laboratories for Materials Science and Technology,
      Überlandstrasse 129, 8600 Dübendorf
      Switzerland
   index: 1
date: 11 January 2022
bibliography: paper.bib
---

# Summary

The management of scientific data is a key aspect of modern data science. Four simple guiding principles that are combined under the FAIR data moniker define the current "gold standard" in data quality: the data has to be **F**indable by anyone, **A**ccessible without barriers,  **I**nteroperable with other programs, and **R**eusable after analysis.~[@Wilkinson2016] Yet, many scientific data formats do not conform to these principles - especially the proprietary formats associated with expensive lab instrumentation. The `yadg` suite of tools helps to resolve this issue by parsing raw data files into a standardised, annotated, timestamped, user-readable format, including information about provenance, units, and measurement uncertainties by default. Various raw data formats are supported, including chromatograms, electrochemical cycling protocols, reflection coefficient traces, spectroscopic traces, and tabulated data. Several standard data processing steps, such as applying calibration functions, integration of chromatographic traces, or fitting of reflection coefficients, are available in `yadg`. 

# Statement of need

From the point of view of catalytic chemistry, digitalisation is currently a "hot topic". For example, the leading German and Swiss academic bodies in the field of catalysis consider digitalisation a key task for the current decade. The German Catalysis Society has published a detailed roadmap,~[@Demtroder2019] and large consorcia have been formed (eg. FAIRmat~[@FAIRmat] in Germany or NCCR Catalysis in Switzerland~[@NCCRcat]) to advance this issue. 

However, this change will not happen overnight. One approach for kick-starting this transition is to make currently existing "small data" available according to the FAIR principles,~[@Mendes2021] effectively defining a "big data" standard by superposition of current best practice. Another approach, more specific to catalysis, is that of standardisation of testing and characterisation protocols,~[@Trunschke2020] which will necessarily lead to standardised data content. The `yadg` package has originally been conceived to combine both of those approaches, and along with a lab automation software and data post-processing tools, forms a robust data scientific pipeline.~[@Kraus2021x]

![Example workflow for `yadg`.\label{fig:workflow}](fig_1.png)

An example workflow for `yadg` is shown in \autoref{fig:workflow}. The devices in the laboratory create raw data files that are different in shape, size, and number. If one wishes to upload this raw data into an electronic lab notebook software (ELN), or use it in postprocessing, the intermediate parsing step is often custom, specific to the particular data files as opposed to file types, and usually manual and hence prone to human error. However, generally it is possible to semantically define a set of raw data related to an experiment, for example by placing them in a folder. Then, a hierarchical description (`schema`) of the data in that folder can be created, containing information about the file types, quantities, their locations, etc. Such a `schema` file can then be reproducibly processed by `yadg` to create a standardised, timestamped, and annotated `datagram` (a machine readable `JSON` file) that can be directly uploaded to the ELN or used in postprocessing. Additionally, the same `schema` can be used to process different experimental folders using the `preset` functionality of `yadg`.

Here, we present the revised `yadg-4.0`. In contrast with the previous version of the tool, raw data is now retained in the `datagram` and is annotated by units and measurement uncertainties. While units are often present in the raw data files, the uncertainties often have to be determined from instrument specification. This is a particularly important feature, as most data scientific packages in the Python ecosystem either support annotating array or tabular data by units (`astropy`~[@astropy] or `pint`~[@pint]), or uncertainties (`unumpy` from the `uncertainties`~[@uncertainties] package); the combination of units and uncertainties is quite rare, especially with non-tabular data.

On the feature front, `yadg-4.0` adds support for several new chromatographic data formats as well as electrochemistry data, among many other formats. For chromatography, several open-source packages for parsing and processing chromatographic data exist, but they are often unmaintained (eg. `PyMS` with last release in 2017,~[@pyms] or `Aston` in 2020~[@aston]) or method specific (`PyMassSpec`~[@pymassspec]). In `yadg`, the main goal is to extract the trace data. Peak integration is optional, using a simple but well defined peak integrator, and a drop-in calibration file functionality, regardless of the type of chromatography or analyte detection used. For electrochemistry, the proprietary file formats supported in `yadg-4.0` have been reverse-engineered: to our knowledge, `yadg` is the only software with a comprehensive parser of such file types.




# Acknowledgements

The authors would like to thank A. Senocrate and F. Bernasconi for discussions and raw data. P.K. would like to thank E. H. Wolf for helpful discussions during previous iterations of this project.

# References