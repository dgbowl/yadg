Key features of **yadg**
------------------------

Units and uncertainties
```````````````````````
One of the key features of **yadg** is the enforced association of units and uncertainties with measured properties. This means that all experimental quantities are accompanied by an uncertainty estimate, derived either from the ``string -> float`` conversion of the data, or from instrumental resolution, if known.

Units
+++++
In the resulting |NetCDF| files, the unit annotations are stored in ``.attrs["units"]`` on each :class:`xarray.DataArray`, that is within each "column" of each "node" of the :class:`~xarray.DataTree`. If an entry does not contain ``.attrs["units"]``, the quantity is dimensionless.

.. warning::

    A special :class:`pint.UnitRegistry` was exposed in ``yadg-4.x`` under :class:`yadg.dgutils.ureg`. Use of this :class:`pint.UnitRegistry` is deprecated as of ``yadg-5.0``, and it will be removed in ``yadg-6.0``.


Uncertainties
+++++++++++++
In many cases it is possible to define more than one uncertainty for each measurement: for example, accuracy, precision, as well as instrument resolution etc. may be available. The convention in **yadg** is that when both a measure of within-measurement uncertainty (resolution) and a cross-measurement error (accuracy) are available, the stored uncertainty corresponds to the instrumental resolution associated with each datapoint, i.e. the resolution. The precision of the measurement (which is normally a higher value than that of the resolution) can be obtained using post-processing, e.g. as a ``mean()`` and ``stdev()`` of a series of data.

Unless more information is available, when converting :class:`str` data to :class:`float`, the uncertainty is determined from the last significant digit specified in the :class:`str`. For this, the functionality from within the |uncertainties|_ package is used.

In the resulting |NetCDF| files, the uncertainties for each ``f"{entry}"`` are stored as a separate data variable, ``f"{entry}_std_err"``. The link between the nominal value and its uncertainty is annotated using ``.attrs["ancillary_variables"] = f"{entry}_std_err"``. The reverse link between the uncertainty and its nominal value is annotated similarly, using ``.attrs["standard_name"] = f"{entry} standard_error"``. This follows the `NetCDF CF Metadata Conventions <https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html>`_, see `Section 3.4 on Ancillary Data <https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#ancillary-data>`_.


Timestamping
````````````
Another key feature in **yadg** is the timestamping of all datapoints. The Unix timestamp is used, as it's the natural timestamp for Python, and with its resolution in seconds it can be easily converted to minutes or hours. All conversions of date and time objects into Unix timestamps are timezone-aware, with the timezone corresponding to the ``localtime`` used as a default.

Most of the supported file formats contain a timestamp of some kind. However, several file formats may not include a complete timestamp, by ommiting either the acquisition date or time, or both. That is why **yadg** includes a powerful "external date" interface, see :func:`~yadg.dgutils.dateutils.complete_timestamps`, which allows you to supply timestamp information externally.


Locale support
``````````````
Support for parsing decimal numbers in localized files is implemented in **yadg** via the :mod:`babel` library, allowing you to specify the locale of the file using standard locale strings, such as ``en_US`` or ``de_CH``. This avoids "hacks" such as replacing decimal separators (``,`` vs ``.``) and thousands separators when processing localizable files. By default, **yadg** attempts to infer the locale from the ``LC_NUMERIC`` environment variable; if this is not set in your environment, ``en_GB`` is used as a fallback.

Note that locale settings currently do not affect processing of date and time strings.


Original metadata
`````````````````
By default, **yadg** attempts to decode and store all understood metadata present in the extracted files. Currently, this metadata is stored in the ``original_metadata`` entry within the ``.attrs`` on the :class:`~xarray.DataTree` nodes, which is serialised into json strings in the :func:`yadg.extractors.extract` function.

.. warning::

    The ``original_metadata`` functionality has been introduced in ``yadg-5.1`` and its implementation might change in future versions.

.. note::

    When merging multiple files into one :class:`~xarray.DataTree`, it may happen that the ``original_metadata`` entry is not identical in between the processed files. In such cases, executing **yadg** with the ``--ignore-merge-errors`` option will drop the conflicting metadata entries and proceed with the processing.


`DataSchema` validation
```````````````````````
Additionally, **yadg** provides `DataSchema` validation and updating functionality, by using the schema models from the :mod:`dgbowl_schemas.yadg.dataschema` package. The schemas are implemented in |Pydantic|_, and are developed in lockstep with **yadg**. This |Pydantic|-based validator class should be used to ensure that the incoming `dataschema` is valid.


.. _pint: https://pint.readthedocs.io/en/stable/

.. |pint| replace:: **pint**

.. _uncertainties: https://pythonhosted.org/uncertainties/

.. |uncertainties| replace:: **uncertainties**

.. _Pydantic: https://pydantic-docs.helpmanual.io/

.. |Pydantic| replace:: **Pydantic**

.. |NetCDF| replace:: ``NetCDF``