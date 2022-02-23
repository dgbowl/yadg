import os
import pickle
import json
import datetime
import dateutil.parser
import logging
import tzlocal
import zoneinfo
import numpy as np
from typing import Callable, Union
from collections.abc import Iterable


def now(
    asstr: bool = False, tz: datetime.timezone = datetime.timezone.utc
) -> Union[float, str]:
    """
    Wrapper around datetime.now()

    A convenience function for returning the current time as a ISO 8601 or as a unix timestamp.
    """
    dt = datetime.datetime.now(tz=tz)
    if asstr:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.timestamp()


def ole_to_uts(ole_timestamp: float, timezone: str = "UTC") -> float:
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
    if timezone == "localtime":
        tz = tzlocal.get_localzone()
    else:
        tz = zoneinfo.ZoneInfo(timezone)

    ole_base = datetime.datetime(year=1899, month=12, day=30, tzinfo=tz)
    ole_delta = datetime.timedelta(days=ole_timestamp)
    time = ole_base + ole_delta
    return time.timestamp()


def str_to_uts(
    timestamp: str, format: str = None, timezone: str = "UTC", strict: bool = True
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
    if timezone == "localtime":
        tz = tzlocal.get_localzone()
    else:
        tz = zoneinfo.ZoneInfo(timezone)

    try:
        if format is None:
            dt = dateutil.parser.parse(timestamp)
        else:
            dt = datetime.datetime.strptime(timestamp, format)

        local_tz = tz if dt.tzinfo is None else dt.tzinfo
        local_dt = dt.replace(tzinfo=local_tz)
        utc_dt = local_dt.astimezone(datetime.timezone.utc)
        return utc_dt.timestamp()
    except (dateutil.parser.ParserError, ValueError) as e:
        if strict:
            raise e
        else:
            logging.info(
                f"str_to_uts: Parsing timestamp '{timestamp}' with "
                f"format '{format}' was not successful."
            )
            return None


def infer_timestamp_from(
    headers: list = None, spec: dict = None, timezone: str = "UTC"
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
        optional formats. Currently accepted combinations of keys are: "uts"; "timestamp";
        "date" and / or "time".

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
        if "uts" in spec:
            return [spec["uts"].get("index", None)], float, True
        if "timestamp" in spec:

            def retfunc(value):
                return str_to_uts(
                    value, spec["timestamp"].get("format", None), timezone=timezone
                )

            return [spec["timestamp"].get("index", None)], retfunc, True
        if "date" in spec or "time" in spec:
            specdict = {
                "date": datetime.datetime.fromtimestamp(0).timestamp,
                "time": datetime.datetime.fromtimestamp(0).timestamp,
            }
            cols = [None, None]
            if "date" in spec:

                def datefn(value):
                    return str_to_uts(
                        value, spec["date"].get("format", None), timezone=timezone
                    )

                cols[0] = spec["date"].get("index", None)
                specdict["date"] = datefn

            if "time" in spec:
                if "format" in spec["time"]:

                    def timefn(value):
                        t = datetime.datetime.strptime(value, spec["time"]["format"])
                        td = datetime.timedelta(
                            hours=t.hour,
                            minutes=t.minute,
                            seconds=t.second,
                            microseconds=t.microsecond,
                        )
                        return td.total_seconds()

                    cols[1] = spec["time"].get("index", None)
                else:
                    logging.debug(
                        "dateutils: Assuming specified column containing the time is in ISO 8601 format"
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

                    cols[1] = spec["time"].get("index", None)
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
        logging.info(
            "dateutils: No timestamp spec provided, assuming column 'uts' is a valid unix timestamp"
        )
        return [headers.index("uts")], float, True
    elif "timestamp" in headers:
        logging.info(
            "dateutils: No timestamp spec provided, assuming column 'timestamp' is a valid ISO 8601 timestamp"
        )

        def retfunc(value):
            return str_to_uts(value, timezone=timezone)

        return [headers.index("timestamp")], retfunc, True
    else:
        assert False, "dateutils: A valid timestamp could not be deduced."


def complete_timestamps(
    timesteps: list, fn: str, spec: dict = {}, timezone: str = "UTC"
) -> None:
    """
    Timestamp completing function.

    This function allows for completing or overriding the uts timestamps determined by
    the individual parsers. **yadg** enters this function for any parser which does not
    return a full timestamp, as well as if the ``externaldate`` specification is
    specified by the user.

    The ``externaldate`` specification is as follows:

    .. code-block:: yaml

        externaldate:
          from:
            file:
                path:    !!str     # path of the external date file
                type:    !!str     # type of the external date file
                match:   !!str     # string to match timestamps with
            isostring:   !!str     # string offset parsed with dateutil
            utsoffset:   !!float   # float offset
            filename:
                format:  !!str     # strptime-style format
                len:     !!int     # length of filename string to match
          mode:          !!str     # "add" or "replace" timestamp

    The ``"from"`` key specifies how an external timestamp is created. Only one entry in
    ``"from"`` is permitted. By default, this entry is:

    .. code-block:: yaml

        externaldate:
          from:
            filename:
              format: "%Y-%m-%d-%H-%M-%S"
              len: 19

    Which means the code will attempt to deduce the timestamp from the path of the
    processed file (``fn``), using the first 19 characters of the base filename
    according to the above format (eg. "2021-12-31-13-45-00").

    If ``"file"`` is specified, the handling of timestamps is handed off to
    :func:`timestamps_from_file`.

    The ``"mode"`` key specifies whether the offsets determined in this function are
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

    defaultmethod = {"filename": {"format": "%Y-%m-%d-%H-%M-%S", "len": 19}}

    replace = spec.get("mode", "add") == "replace"
    methods = spec.get("from", defaultmethod)

    delta = None

    if "file" in methods:
        method = methods["file"]
        delta = timestamps_from_file(method["path"], method["type"], timezone)
    elif "isostring" in methods:
        delta = str_to_uts(methods["isostring"], None, timezone, True)
    elif "utsoffset" in methods:
        delta = float(methods["utsoffset"])
    elif "filename" in methods:
        method = methods["filename"]
        dirname, basename = os.path.split(fn)
        filename, ext = os.path.splitext(basename)
        ls = method.get("len", len(filename))
        delta = str_to_uts(filename[:ls], method["format"], timezone, False)

    if delta is None:
        logging.info("complete_timestamps: Timestamp completion failed. Using mtime.")
        delta = os.path.getmtime(fn)

    if isinstance(delta, float):
        delta = [delta] * len(timesteps)

    assert len(delta) == len(timesteps)

    for ts in timesteps:
        if replace:
            ts["uts"] = delta.pop(0)
        else:
            ts["uts"] = ts.get("uts", 0.0) + delta.pop(0)


def timestamps_from_file(path: str, type: str, timezone: str = "UTC") -> list[float]:
    """
    Load timestamps from file.

    This function enables loading timestamps from file. The currently supported
    file formats include ``json`` and ``pkl``, which must contain a top-level
    :class:`(Iterable)` of :class:`(str)` or :class:`(float)`-like objects.

    Parameters
    ----------
    path
        Location of the external file.

    type
        Type of the external file. Currently, ``"json", "pkl"`` are supported.

    timezone
        An optional timezone string, defaults to "UTC"

    Returns
    -------
    parseddata: list[float]
        A list of POSIX timestamps.

    """
    assert os.path.exists(path), f"timestamps_from_file: path '{path}' doesn't exist."
    assert os.path.isfile(path), f"timestamps_from_file: Path '{path}' is not a file."

    if type == "pkl":
        logging.info(f"timestamps_from_file: loading '{path}' as pickle.")
        with open(path, "rb") as infile:
            data = pickle.load(infile)
    elif type == "json":
        logging.info(f"timestamps_from_file: loading '{path}' as json.")
        with open(path, "r") as infile:
            data = json.load(infile)
    elif type == "agilent.log":
        logging.critical(f"timestamps_from_file: type 'agilent.log' not yet supported.")
        data = None

    if data is None:
        return data
    elif isinstance(data, Iterable):
        parseddata = []
        for i in data:
            if isinstance(i, str):
                delta = str_to_uts(i, None, timezone, True)
                parseddata.append(delta)
            elif isinstance(i, (int, float, np.number)):
                parseddata.append(float(i))
        return parseddata
