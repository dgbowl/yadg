What is a `datagram`
````````````````````
The `datagram` is a structured and annotated representation of raw and processed
data. Here, "raw data" corresponds to data present in the instrument output files
directly, and "processed data" corresponds to data after any processing -- whether
it is applying a calibration curve, or a more involved transformation, such as
deriving :math:`Q_0` and :math:`f_0` from :math:`\Gamma(f)` in the
:mod:`yadg.parsers.qftrace` module.

The `datagram` can then be consumed by other post-processing utilities.

Futher information about the `datagram` can be found in the documentation of the
`datagram` validator function: :func:`yadg.core.validators.validate_datagram`.