---
title: 'yadg: yet another datagram'
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
date: 20 January 2022
bibliography: paper.bib
---

# Summary

The management of scientific data is a crucial aspect of modern data science. Four simple guiding principles combined under the FAIR data moniker define the current "gold standard" in data quality: the data has to be **F**indable by anyone, **A**ccessible without barriers,  **I**nteroperable with other programs, and **R**eusable after analysis [@Wilkinson2016]. Yet, many scientific data formats do not conform to these principles. This is especially true for proprietary formats, often associated with expensive lab instrumentation. The `yadg` package helps to resolve this issue by parsing raw data files into a standardised, annotated and timestamped format readable by both humans and machines. Various raw data formats are supported, including chromatograms, electrochemical cycling protocols, reflection coefficient traces, spectroscopic data, and tabulated data. The parsed files include information about data provenance, units of measure, and experimental uncertainties by default. Finally, several common data processing steps, such as applying calibration functions, integration of chromatographic traces, or fitting of reflection coefficients, are available in `yadg`. 

# Statement of need

From the point of view of catalytic chemistry, digitalisation is currently a "hot topic". For example, the leading German and Swiss academic bodies in the field of catalysis consider digitalisation an essential task for the current decade. The German Catalysis Society has published a detailed roadmap [@Demtroder2019], and large consortia have been formed (eg. FAIRmat [@Draxl2020] in Germany or NCCR Catalysis in Switzerland [@NCCRcat]) to advance this issue. 

However, this change will not happen overnight. One approach for kick-starting this transition is to make the currently existing "small data" available according to the FAIR principles [@Mendes2021], effectively defining a standard for "big data" by superposition of current best practices. Another approach, more specific to catalysis, is that of standardisation of testing and characterisation protocols [@Trunschke2020], which will necessarily lead to a standardised data content. The `yadg` package presented here has been conceived to combine both approaches, and when combined with a lab automation software and data post-processing tools, forms a robust data-scientific pipeline [@Kraus2021x].

![Example workflow for `yadg`.\label{fig:workflow}](fig_1.png){width=75%}

An example laboratory workflow is shown in \autoref{fig:workflow}. The devices in the laboratory (eg. chromatographs, flow meters, potentiostats, temperature controllers, or spectrometers) create raw data files that are different in shape, size, and number. If one wishes to store this raw data in an electronic lab notebook (ELN) software in a FAIR way or use it in post-processing, the raw data must be parsed. The intermediate parsing step is often not standardised: in the case of chromatography, the data parsing may be specific to the particular data files as opposed to file types, and in the case of flow and temperature data the values are often entered manually and hence prone to human error. 

However, it is generally possible to semantically define a set of raw data related to an experiment by placing them in a folder. Then, a hierarchical description (`schema`) of the data in that folder can be created, containing information about the file types, quantities, their locations, etc. The `yadg` package can be used for reproducible processing of such `schema` files into a standardised, timestamped, versioned, annotated, and validated `datagram`, which can be directly uploaded to the ELN or used in post-processing. The file parsers in `yadg` are written in a modular fashion, grouped by scientific application (e.g. chromatography, electrochemistry, etc.), and are fully transparent to the user regardless of the raw file format or device vendor. Additionally, the same `schema` can be used to process different experimental folders using the `preset` functionality of `yadg`.

# Features
Here, we present the revised `yadg-4.0`. Compared to the previous version of `yadg` [@Kraus2021x], the three main user-facing changes in `yadg-4.0` include units and uncertainties in the raw data, the enhanced chromatogram parser functionality, and the new electrochemistry parser. For a more detailed list of changes, please see the [release notes](https://dgbowl.github.io/yadg/4.0.0/version.html#yadg-version-4-0-0). 

## Usage
An interactive, Binder-ready Jupyter notebook, illustrating the installation and usage of `yadg-4.0`, is included on Zenodo under [DOI: 10.5281/zenodo.6351210](https://doi.org/10.5281/zenodo.6351210). The Binder-ready notebook can be launched by following [this link](https://mybinder.org/v2/zenodo/10.5281/zenodo.6351210/?labpath=index.ipynb).

## Units and uncertainties
In contrast with the previous version of the tool, raw data is now retained in the `datagram` and is annotated by units and measurement uncertainties, making `datagrams` suitable for archiving in an ELN. While units are often present in the raw data files, the uncertainties often have to be determined from instrument specifications. This is a particularly important feature, as most data scientific packages in the Python ecosystem either support annotating array or tabular data by units ([`astropy`](https://www.astropy.org/) [@astropy;@TheAstropyCollaboration2018] or [`pint`](https://pint.readthedocs.io/en/stable/) [@pint]), or uncertainties ([`unumpy`](https://pythonhosted.org/uncertainties/numpy_guide.html) from the [`uncertainties`](https://pythonhosted.org/uncertainties/index.html) package  [@uncertainties]); the combination of both units and uncertainties is quite rare, especially with non-tabular data.

## Chromatography
The new version of `yadg` adds support for several new chromatographic data formats. Several open-source packages for parsing and processing chromatographic data exist, but they are often unmaintained (eg. [`PyMS`](https://code.google.com/archive/p/pyms/) [@pyms;@OCallaghan2012], or [`Aston`](https://github.com/bovee/Aston) [@aston]) or they are specialised for a single branch of chromatography, such as [`PyMassSpec`](https://pymassspec.readthedocs.io/en/master/) [@pymassspec]. For `yadg`, the main goal is to parse the often proprietary and binary formats and extract the trace data. The parser now supports several new formats, including Agilent's `.ch` and `.dx` file types, the parsing of which is based on the Matlab routines available in the [`chromatography`](https://github.com/chemplexity/chromatography) repository [@chromatography].

The peak integration in `yadg` has been completely re-written and is now extensively using `numpy.ndarrays` [@Harris2020]. Combined with a drop-in calibration file functionality, `yadg` is a powerful chromatogram processing tool, usable regardless of the type of chromatography or detector used.

## Electrochemistry
Another major feature in `yadg-4.0` is the support for electrochemical data. Files containing data from basic electrochemical techniques (chronoamperometry, chronopotentiometry, linear sweep voltammetry), two- or three-electrode experiments, battery cycling protocols, or impedance methods (potentio- and galvano-electrochemical impedance spectroscopy) are supported, among many other techniques. As with other file types, the electrochemistry data is fully annotated with units and uncertainties based on instrument specifications. 

The proprietary file formats supported in `yadg-4.0` have been reverse-engineered. This work was inspired by the [`galvani`](https://github.com/echemdata/galvani) package [@galvani]. The parser in `yadg-4.0` also processes the metadata and settings stored in the binary `.mpr` files, supports parsing of text `.mpt` files, and supports a much wider range of instruments and electrochemical techniques, making `yadg` the most complete open-source parser for such file types.

## Forwards compatibility
File types supported in the previous version of `yadg` are still supported in the current version. Starting with `yadg-4.0`, an update path for `schema` files is available, meaning old `schema` files containing or referencing calibration data in superseded formats can be seamlessly migrated to the latest version of `yadg`.

# Acknowledgements
The authors acknowledge funding from the Synfuels project of the ETH Board. The authors would like to thank A. Senocrate and F. Bernasconi for discussions and raw data files. P. K. would like to thank E. H. Wolf for helpful discussions during previous iterations of this project.

# References
