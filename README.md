[![DOI](https://joss.theoj.org/papers/10.21105/joss.04166/status.svg)](https://doi.org/10.21105/joss.04166)
[![Documentation](https://badgen.net/badge/docs/dgbowl.github.io/grey?icon=firefox)](https://dgbowl.github.io/yadg)
[![PyPi version](https://badgen.net/pypi/v/yadg/?icon=pypi)](https://pypi.org/project/yadg)
![Github link](https://badgen.net/github/tag/dgbowl/yadg/?icon=github)
![Github status](https://badgen.net/github/checks/dgbowl/yadg/?icon=github)
[![LGTM analysis](https://badgen.net/lgtm/grade/g/dgbowl/yadg/python/?logo=lgtm)](https://lgtm.com/projects/g/dgbowl/yadg/context:python)


# ![yet another datagram](./docs/source/images/yadg_banner.png)

Set of tools to process raw instrument data according to a *dataschema* into a standardised form called *datagram*, annotated with metadata, provenance information, timestamps, units, and uncertainties. Developed by the [Materials for Energy Conversion](https://www.empa.ch/web/s501) at Empa - Materials Science and Technology.

![schema to datagram with yadg](./docs/source/images/schema_yadg_datagram.png)

### Capabilities:
- Parsing **tabulated data** using CSV parsing functionality, including Bronkhorst and DryCal output formats. Columns can be post-processed using any linear combinations of raw and processed data using the calibration functionality.
- Parsing **chromatography data** from gas and liquid chromatography, including several Agilent, Masshunter, and Fusion formats. If a calibration file is provided, the traces are automatically integrated using built-in integration routines.
- Parsing **reflection coefficient** traces from network analysers. The raw data can be fitted to obtain the quality factor and central frequency using several algorithms.
- Parsing **potentiostat files** for electrochemistry applications. Supports BioLogic file formats.

### Features:
- timezone-aware timestamping using Unix timestamps
- automatic uncertainty determination using data contained in the raw files, instrument specification, or last significant digit
- uncertainty propagation to derived quantities
- tagging of data with units
- extensive *dataschema* and *datagram* validation using provided specifications
- mandatory metadata (such as provenance) is enforced

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
