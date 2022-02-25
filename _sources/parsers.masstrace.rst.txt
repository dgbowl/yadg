``masstrace``: Mass spectrometry parser
=======================================
The ``masstrace`` parser handles the reading and processing of mass
spectrometry files. The basic function of the parser is to:

1) read in the raw data and create timestamped `traces`
2) collect `metadata` such as the software version, author, etc.

Usage
-----
The use of ``masstrace`` can be specified using the ``"parser"`` keyword
in the `schema`. Further information can be specified in the
``"parameters"`` :class:`(dict)`:

- ``"tracetype"`` :class:`(str)`: The file type of the raw data file.
  See :ref:`here<parsers_masstrace_formats>` for details.

.. _parsers_masstrace_provides:

Provides
--------
The primary functionality of ``masstrace`` is to load mass spectrometry
data, including determining uncertainties of the signal (y-axis), as
well as explicitly populating the points in the mass axis (``m/z``).
This raw data is stored, for each timestep, in the ``"raw"`` entry using
the following format:

.. code-block:: yaml

    - raw:
        traces:
          "{{ trace_number }}":  # number of the trace
            y_title: !!str       # y-axis label from file
            comment: !!str       # comment
            fsr:     !!str       # full scale range of the detector
            m/z:                 # masses are always in amu
              {n: [!!float, ...], s: [!!float, ...], u: "amu"}
            y:                   # y-axis units from file
              {n: [!!float, ...], s: [!!float, ...], u: !!str}

The uncertainties ``"s"`` in ``"m/z"`` are taken as the step-width of
the linearly spaced mass values.

The uncertainties ``"s"`` of ``"y"`` are the largest value between:

#. The quantization error from the ADC, its resolution assumed to be 32
   bit. Dividing F.S.R. by ``2 ** 32`` gives an error in the order of
   magnitude of the smallest data value in ``"y"``.
#. The contribution from neighboring masses. In the operating manual of
   the QMS 200 (see 2.8 QMS 200 F & 2.9 QMS 200 M), a maximum
   contribution from the neighboring mass of 50 ppm is noted.

.. note::

    The data in ``"y"`` may contain ``NaN`` s. The measured ion
    count/current value will occasionally exceed the specified detector
    F.S.R. (e.g. 1e-9), and will then flip directly to the maximum value
    of a float32. These values are set to ``float("NaN")``.

The ``"metadata"`` collected from the raw file will depend on the
``"tracetype"``. In general, the following metadata entries are stored
in the ``"params"`` element of each `step`:

.. code-block:: yaml

    params:
      software_id:  !!int  # software ID
      version:      !!str  # software version
      username:     !!str  # file author
