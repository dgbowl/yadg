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
 - name: Empa - Swiss Federal Laboratories for Materials Science and Technology
   index: 1
date: 11 January 2022
bibliography: paper.bib
---

# Summary

The management of scientific data is a key aspect of modern data science. Four simple guiding principles describe the so-called FAIR data standard: the data has to be **F**indable by anyone, **A**ccessible without barriers,  **I**nteroperable with other programs, and **R**eusable after analysis.[@Wilkinson2016] Yet, many scientific data formats do not conform to these principles. The `yadg` suite of tools resolves this issue by parsing raw data files into a standardised, annotated, timestamped, user-readable format, including information about provenance, units, and measurement uncertainties by default. Various raw data formats are supported, including chromatograms, electrochemical cycling protocols, reflection coefficient traces, spectroscopic traces, and tabulated data. Several standard data processing steps, such as applying calibration functions, integration of chromatographic traces, or fitting of reflection coefficients, are available in `yadg`. 

# Statement of need

From the point of view of catalytic chemistry, digitalisation is currently a "hot topic". Both the German Catalysis Society (GeCatS) and the Swiss National Centre for Competence in Research in Catalysis (NCCR Catalysis) consider digitalisation of catalysis a key task for the current decade.[@Demtroder2019;@NCCRcat] However, this change will not happen overnight. One approach for tackling this transition is to make "small data" available according to the FAIR principles.[@Mendes2021] Another approach it that of standardisation of testing and characterisation protocols, which will necessarily lead to standardised data content.[@Trunschke2020] The `yadg` package has originally been conceived to combine both of those approaches, and along with a lab automation software and data post-processing tools, forms a robust data scientific pipeline.[@Kraus2021x]



`Gala` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for `Gala` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. `Gala` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

`Gala` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in `Gala` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike.

# Acknowledgements

The authors would like to thank A. Senocrate and F. Bernasconi for discussions and raw data. P.K. would like to thank E. H. Wolf for helpful discussions during previous iterations of this project.

# References