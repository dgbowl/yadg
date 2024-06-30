import os
import pickle
import json
import datetime
import dateutil.parser
import logging
from zoneinfo import ZoneInfo
import numpy as np
from pydantic import BaseModel
from typing import Callable, Union, Mapping, Iterable
from xarray import Dataset
from dgbowl_schemas.yadg.dataschema_5_0.externaldate import ExternalDate
from dgbowl_schemas.yadg.dataschema_5_0.timestamp import TimestampSpec


logger = logging.getLogger(__name__)


def now(
    asstr: bool = False, tz: datetime.timezone = datetime.timezone.utc
) -> Union[float, str]:
    """
    Wrapper around datetime.now()

    A convenience function for returning the current time as a ISO 8601 or as a Unix
    timestamp.
    """
    dt = datetime.datetime.now(tz=tz)
    if asstr:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.timestamp()


def ole_to_uts(ole_timestamp: float, timezone: str) -> float:
    """
    Converts a Microsoft OLE timestamp into a POSIX timestamp.

    The OLE automation date format is a floating point value, counting
    days since midnight 30 December 1899. Hours and minutes are
    represented as fractional days.

    https://devblogs.microsoft.com/oldnewthing/20030905-02/?p=42653

    Parameters
    ----------
    ole_timestamp
        A timestamp in Microsoft OLE format.
    timezone
        String desribing the timezone.

    Returns
    -------
    time: float
        The corresponding Unix timestamp.

    """
    tzinfo = ZoneInfo(timezone)
    ole_base = datetime.datetime(year=1899, month=12, day=30, tzinfo=tzinfo)
    ole_delta = datetime.timedelta(days=ole_timestamp)
    time = ole_base + ole_delta
    return time.timestamp()


def str_to_uts(
    *,
    timestamp: str,
    timezone: str,
    format: str = None,
    strict: bool = True,
) -> Union[float, None]:
    """
    Converts a string to POSIX timestamp.

    If the optional ``format`` is specified, the ``timestamp`` string is processed
    using the :func:`datetime.datetime.strptime` function; if no ``format`` is
    supplied, an ISO 8601 format is assumed and an attempt to parse using
    :func:`dateutil.parser.parse` is made.

    Parameters
    ----------
    timestamp
        A string containing the timestamp.

    format
        Optional format string for parsing of the ``timestamp``.

    timezone
        Optional timezone of the ``timestamp``. By default, "UTC".

    strict
        Whether to re-raise any parsing errors.

    Returns
    -------
    uts: Union[float, None]
        Returns the POSIX timestamp if successful, otherwise None.

    """

    try:
        if format is None:
            dt = dateutil.parser.parse(timestamp)
        else:
            dt = datetime.datetime.strptime(timestamp, format)

        local_tz = ZoneInfo(timezone) if dt.tzinfo is None else dt.tzinfo
        local_dt = dt.replace(tzinfo=local_tz)
        utc_dt = local_dt.astimezone(datetime.timezone.utc)
        return utc_dt.timestamp()
    except (dateutil.parser.ParserError, ValueError) as e:
        if strict:
            raise e
        else:
            logger.info(
                "Parsing timestamp '%s' with format '%s' was not successful.",
                str(timestamp),
                format,
            )
            return None


def infer_timestamp_from(
    *,
    headers: list = None,
    spec: TimestampSpec = None,
    timezone: str,
) -> tuple[list, Callable, bool]:
    """
    Convenience function for timestamping

    Given a set of headers, and an optional specification, return an array containing
    column indices from which a timestamp in a given row can be computed, as well as the
    function which will compute the timestamp given the returned array.

    Parameters
    ----------
    headers
        An array of strings. If `spec` is not supplied, must contain either "uts"
        :class:`(float)` or "timestep" :class:`(str)` (conforming to ISO 8601).

    spec
        A specification of timestamp elements with associated column indices and
        optional formats. Currently accepted combinations of keys are: "uts";
        "timestamp"; "date" and / or "time".

    tz
        Timezone to use for conversion. By default, UTC is used.

    Returns
    -------
    (datecolumns, datefunc, fulldate): tuple[list, Callable, bool]
        A tuple containing a list of indices of columns, a Callable to which the
        columns have to be passed to obtain a uts timestamp, and whether the determined
        timestamp is full or partial.

    """

    if spec is not None:
        if hasattr(spec, "uts"):
            return [spec.uts.index], float, True
        elif hasattr(spec, "timestamp"):

            def retfunc(value):
                return str_to_uts(
                    timestamp=value, format=spec.timestamp.format, timezone=timezone
                )

            return [spec.timestamp.index], retfunc, True
        elif hasattr(spec, "date") or hasattr(spec, "time"):
            specdict = {
                "date": datetime.datetime.fromtimestamp(0).timestamp,
                "time": datetime.datetime.fromtimestamp(0).timestamp,
            }
            cols = [None, None]
            if spec.date is not None:

                def datefn(value):
                    return str_to_uts(
                        timestamp=value, format=spec.date.format, timezone=timezone
                    )

                cols[0] = spec.date.index
                specdict["date"] = datefn
            if spec.time is not None:
                if spec.time.format is not None:

                    def timefn(value):
                        t = datetime.datetime.strptime(value, spec.time.format)
                        td = datetime.timedelta(
                            hours=t.hour,
                            minutes=t.minute,
                            seconds=t.second,
                            microseconds=t.microsecond,
                        )
                        return td.total_seconds()

                else:
                    logger.debug(
                        "Assuming specified column is time in ISO 8601 format."
                    )

                    def timefn(value):
                        t = datetime.time.fromisoformat(value)
                        td = datetime.timedelta(
                            hours=t.hour,
                            minutes=t.minute,
                            seconds=t.second,
                            microseconds=t.microsecond,
                        )
                        return td.total_seconds()

                cols[1] = spec.time.index
                specdict["time"] = timefn
            if cols[0] is None:
                return [cols[1]], specdict["time"], False
            elif cols[1] is None:
                return [cols[0]], specdict["date"], False
            else:

                def retfn(date, time):
                    return specdict["date"](date) + specdict["time"](time)

                return cols, retfn, True
    elif "uts" in headers:
        logger.debug("Assuming column 'uts' is a valid unix timestamp.")
        return [headers.index("uts")], float, True
    elif "timestamp" in headers:
        logger.debug("Assuming column 'timestamp' is a valid ISO 8601 timestamp")

        def retfunc(value):
            return str_to_uts(timestamp=value, timezone=timezone)

        return [headers.index("timestamp")], retfunc, True
    else:
        assert False, "dateutils: A valid timestamp could not be deduced."


def complete_timestamps(
    *,
    timesteps: list,
    fn: str,
    spec: ExternalDate,
    timezone: str,
) -> list[float]:
    """
    Timestamp completing function.

    This function allows for completing or overriding the uts timestamps determined by
    the individual parsers. **yadg** enters this function for any parser which does not
    return a full timestamp, as well as if the ``externaldate`` specification is
    specified by the user.

    The ``externaldate`` specification is as follows:

    .. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.externaldate.ExternalDate
       :noindex:

    The ``using`` key specifies how an external timestamp is created. Only one entry in
    ``using`` is permitted. By default, this entry is:

    .. code-block:: yaml

        using:
          filename:
            format: "%Y-%m-%d-%H-%M-%S"
            len: 19

    Which means the code will attempt to deduce the timestamp from the path of the
    processed file (``fn``), using the first 19 characters of the base filename
    according to the above format (eg. "2021-12-31-13-45-00").

    If ``file`` is specified, the handling of timestamps is handed off to
    :func:`timestamps_from_file`.

    The ``mode`` key specifies whether the offsets determined in this function are
    added to the current timestamps (eg. date offset being added to time) or whether
    they should replace the existing timestamps completely.

    As a measure of last resort, the ``mtime`` of the ``fn`` is used. ``mtime`` is
    preferred to ``ctime``, as the former has a more consistent cross-platform
    behaviour.

    Parameters
    ----------
    timesteps
        A list of timesteps generated from a single file, ``fn``.

    fn
        Filename used to create ``timesteps``.

    spec
        ``externaldate`` specification part of the `schema`.

    timezone
        Timezone, defaults to "UTC".

    """
    delta = None

    fulldate = True
    if spec is not None:
        replace = spec.mode == "replace"
        method = spec.using
    else:
        replace = False
        method = None

    if hasattr(method, "file"):
        delta = timestamps_from_file(
            method.file.path, method.file.type, method.file.match, timezone
        )
    elif hasattr(method, "isostring"):
        delta = str_to_uts(
            timestamp=method.isostring, format=None, timezone=timezone, strict=True
        )
    elif hasattr(method, "utsoffset"):
        delta = method.utsoffset
    elif hasattr(method, "filename"):
        basename = os.path.basename(fn)
        filename, ext = os.path.splitext(basename)
        string = filename[: method.filename.len]
        delta = str_to_uts(
            timestamp=string,
            format=method.filename.format,
            timezone=timezone,
            strict=False,
        )

    if delta is None:
        logger.warning("Timestamp completion failed. Using 'mtime'.")
        delta = os.path.getmtime(fn)
        fulldate = False

    if isinstance(delta, float):
        delta = [delta] * len(timesteps)

    assert len(delta) == len(timesteps)

    if replace:
        timesteps = delta
    else:
        timesteps = timesteps + delta

    return timesteps, fulldate


def timestamps_from_file(
    path: str,
    type: str,
    match: str,
    timezone: str,
) -> Union[float, list[float]]:
    """
    Load timestamps from file.

    This function enables loading timestamps from file specified by the ``path``.
    The currently supported file formats include ``json`` and ``pkl``, which must
    contain a top-level :class:`Mapping` with a key that is matched by ``match``,
    or a top-level :class:`Iterable`, both containing :class:`str` or :class:`float`
    -like objects that can be processed into an Unix timestamp.

    Parameters
    ----------
    path
        Location of the external file.

    type
        Type of the external file. Currently, ``"json", "pkl"`` are supported.

    match
        An optional key to match if the object in ``path`` is a :class:`Mapping`.

    timezone
        An optional timezone string, defaults to "UTC"

    Returns
    -------
    parseddata: Union[float, list[float]]
        A single or a list of POSIX timestamps.

    """
    assert os.path.exists(path), f"timestamps_from_file: path '{path}' doesn't exist."
    assert os.path.isfile(path), f"timestamps_from_file: Path '{path}' is not a file."

    if type == "pkl":
        logger.debug("Loading '%s' as pickle.", path)
        with open(path, "rb") as infile:
            data = pickle.load(infile)
    elif type == "json":
        logger.debug("Loading '%s' as json.", path)
        with open(path, "r") as infile:
            data = json.load(infile)
    elif type == "agilent.log":
        logger.critical("Type 'agilent.log' not yet supported.")
        data = None

    if data is None:
        return data
    elif isinstance(data, Iterable):
        if isinstance(data, Mapping):
            assert match in data
            data = data[match]
        if isinstance(data, Iterable):
            parseddata = []
            for i in data:
                if isinstance(i, str):
                    delta = str_to_uts(
                        timestamp=i, format=None, timezone=timezone, strict=True
                    )
                    parseddata.append(delta)
                elif isinstance(i, (int, float, np.number)):
                    parseddata.append(float(i))
            return parseddata
        else:
            if isinstance(data, str):
                return str_to_uts(
                    timestamp=data, format=None, timezone=timezone, strict=True
                )
            else:
                return float(data)


def complete_uts(
    ds: Dataset,
    filename: str,
    externaldate: BaseModel,
    timezone: str,
) -> Dataset:
    """
    A helper function ensuring that the Dataset ``ds`` contains a dimension ``"uts"``,
    and that the timestamps in ``"uts"`` are completed as instructed in the
    ``externaldate`` specification.

    """
    if not hasattr(ds, "uts"):
        ds = ds.expand_dims("uts")
    if len(ds.uts.coords) == 0:
        ds["uts"] = np.zeros(ds.uts.size)
        ds.attrs["fulldate"] = 0

    # fulldate should be an int, as it's converted int yadg.extract.extract_from_path()
    if ds.attrs.get("fulldate", 1) == 0 or externaldate is not None:
        ts, fulldate = complete_timestamps(
            timesteps=ds.uts.values,
            fn=filename,
            spec=externaldate,
            timezone=timezone,
        )
        ds["uts"] = ts
        if fulldate:
            ds.attrs.pop("fulldate", None)
    return ds
