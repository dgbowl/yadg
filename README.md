[![DOI](https://joss.theoj.org/papers/10.21105/joss.04166/status.svg)](https://doi.org/10.21105/joss.04166)
[![Documentation](https://badgen.net/badge/docs/dgbowl.github.io/grey?icon=firefox)](https://dgbowl.github.io/yadg)
[![PyPi version](https://badgen.net/pypi/v/yadg/?icon=pypi)](https://pypi.org/project/yadg)
[![Github link](https://badgen.net/github/tag/dgbowl/yadg/?icon=github)](https://github.com/dgbowl/yadg/)
[![Github status](https://badgen.net/github/checks/dgbowl/yadg/?icon=github)](https://github.com/dgbowl/yadg/actions/workflows/push-master.yml)


# ![yet another datagram](./docs/source/images/yadg_banner.png)

A set of tools to *extract* raw data from scientific instruments into standardised [`DataTree`](https://xarray-datatree.readthedocs.io/en/latest/) in-memory objects, or into [`NetCDF`](https://www.unidata.ucar.edu/software/netcdf/) files on disk. The resulting data is annotated with metadata, provenance information, timestamps, units, and uncertainties. Currently developed at the [ConCat lab](https://www.tu.berlin/en/concat) at Technische Universität Berlin (Berlin, DE) and the [Materials for Energy Conversion](https://www.empa.ch/web/s501) lab at Empa (Dübendorf, CH).

### Capabilities:
- Extraction of **chromatography data** from gas and liquid chromatograms. Supports several Agilent, EZChrom, Masshunter, and Fusion formats.
- Extraction of **electrochemical data** from electrochemistry and battery cycling experiments. Supports BioLogic file formats.
- Extraction of **reflection coefficient** traces from network analysers. Supports the Touchstone file format.
- Extraction of **spectroscopy files** including common XPS, XRD and MS formats.
- Extraction of **tabulated data** using CSV parsing functionality, including Bronkhorst and DryCal output formats.

Additionally, data from multiple files of the same type, or even of different types, can be easily and reproducibly combined into a single `DataTree` by using *process* and *preset* modes of **yadg**.

### Features:
- timezone-aware timestamp processing using Unix timestamps
- locale-aware processing of files
- automatic uncertainty determination using data contained in the raw files, instrument specification, or last significant digit
- tagging of all data with units
- annotation with processing metadata (such as provenance or extraction date) under the `yadg_⋅⋅⋅` namespace
- original metadata from the extracted files is stored under `original_metadata`
- extensive *dataschema* validation using provided specifications


The full list of capabilities and features is listed in the [project documentation](http://dgbowl.github.io/yadg).

### Installation:
The released versions of `yadg` are available on the Python Package Index (PyPI) under [yadg](https://pypi.org/project/yadg). Those can be installed using:

```bash
    pip install yadg
```

If you wish to install the current development version as an editable installation, check out the `master` branch using git, and install `yadg` as an editable package using pip:

```bash
   git clone git@github.com:dgbowl/yadg.git
   cd yadg
   pip install -e .
```

Additional targets `yadg[testing]` and `yadg[docs]` are available and can be specified in the above commands, if testing and/or documentation capabilities are required.

### Contributors:
- [Peter Kraus](http://github.com/PeterKraus)
- [Nicolas Vetsch](http://github.com/vetschn)

### Acknowledgements

This project has received funding from the following sources:

- European Union’s Horizon 2020 programme under grant agreement No 957189.
- DFG's Emmy Noether Programme under grant number 490703766.

The project is also part of BATTERY 2030+, the large-scale European research initiative for inventing the sustainable batteries of the future.
