**xrdtrace**: X-ray diffractogram parser
========================================
The :mod:`~yadg.parsers.xrdtrace` parser handles the reading and processing of 
X-ray diffraction data.

Usage
-----
The use of :mod:`~yadg.parsers.xrdtrace` can be specified using the ``"parser"`` 
keyword in the `dataschema`. The following information can be specified in the
``"parameters"`` :class:`(dict)`:

- ``"filetype"`` :class:`(str)`: The file type of the raw data file.
  See :ref:`the list of supported formats<parsers_xrdtrace_formats>` for details.

.. _parsers_xrdtrace_provides:

Provides
--------
The primary functionality of :mod:`~yadg.parsers.xrdtrace` is to load X-ray 
diffraction data, and determine reasonable uncertainties of the signal intensity 
(y-axis), as well as populate the angle axis (:math:`2\theta`), if necessary. This 
raw data is stored, for each timestep, in the ``"raw"`` entry using the following 
format:

.. code-block:: yaml

    - raw:
        traces:
          "{{ trace_number }}":   # number of the trace
            angle:                
              {n: [!!float, ...], s: [!!float, ...], u: "deg"}
            intensity:
              {n: [!!float, ...], s: [!!float, ...], u: "counts"}

The uncertainties ``"s"`` in ``"angle"`` are taken as the step-width of
the linearly spaced :math:`2\theta` values.

The uncertainties ``"s"`` of ``"intensity"`` are currently set to a constant
value of ``1.0`` counts as all the supported files seem to produce integer values.

.. warning::
  
  The ``"metadata"`` collected from the raw data file depends on the filetype, and 
  is currently not strictly defined.
