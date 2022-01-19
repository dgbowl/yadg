``xpstrace``: X-ray photoelectron spectroscopy parser
=====================================================
The ``xpstrace`` parser handles the reading and processing of x-ray
photoelectron spectroscopy files. The basic function of the parser is
to:

1) read in the raw data and create timestamped `traces`
2) collect `metadata` such as measurement settings, software, operator
   etc.

Usage
-----
The use of ``xpstrace`` can be specified using the ``"parser"`` keyword
in the `schema`. Further information can be specified in the
``"parameters"`` :class:`(dict)`:

- ``"tracetype"`` :class:`(str)`: The file type of the raw data file.
  See :ref:`here<parsers_xpstrace_formats>` for details.

.. _parsers_xpstrace_provides:

Provides
--------
The primary functionality of ``xpstrace`` is to load x-ray photoelectron
spectroscopy data, including determining uncertainties of the signal
(y-axis), as well as explicitly populating the points in the energy axis
(``E``). This raw data is stored, for each timestep, in the ``"raw"``
entry using the following format:

.. code-block:: yaml

    - raw:
        traces:
          "{{ trace_number }}":   # number of the trace
            name:          !!str  #
            atomic_number: !!str  #
            dwell_time:    !!str  #
            e_pass:        !!str  #
            description:   !!str  #
            E:                    # energies are always in eV
              {n: [!!float, ...], s: [!!float, ...], u: "eV"}
            y:                   # y-axis units from file
              {n: [!!float, ...], s: [!!float, ...], u: !!str}

The uncertainties ``"s"`` in ``"E"`` are taken as the step-width of
the linearly spaced energy values.

The uncertainties ``"s"`` of ``"y"`` are currently set to a constant
value of ``12.5`` counts per second as all the signals in the files seen so
far only seem to take on values in those steps.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/13

    Determining the uncertainty of the counts per second signal in xps
    traces from the phispe parser should be done in a better way.

In general, the ``"metadata"`` collected from the raw file will depend
on the ``"tracetype"``. The following metadata entries are definitely
stored in the ``"params"`` element of each `step`:

.. code-block:: yaml

    params:
      software_id:  !!str  # software name
      version:      !!str  # software version
      username:     !!str  # operator
