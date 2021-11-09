import datetime
import dateutil.parser
import tzlocal
import zoneinfo
import logging
from typing import Callable, Union
import os


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


def ole_to_uts(ole_timestamp: float) -> float:
    """Converts a Microsoft OLE timestamp into a POSIX timestamp.

    The OLE automation date format is a floating point value, counting
    days since midnight 30 December 1899. Hours and minutes are
    represented as fractional days.

    https://devblogs.microsoft.com/oldnewthing/20030905-02/?p=42653

    Parameters
    ----------
    ole_timestamp
        A timestamp in Microsoft OLE format.

    Returns
    -------
    float
        The corresponding Unix timestamp.

    """
    ole_base = datetime.datetime(year=1899, month=12, day=30)
    ole_delta = datetime.timedelta(days=ole_timestamp)
    time = ole_base + ole_delta
    return time.timestamp()


def infer_timestamp_from(
    headers: list = None, spec: dict = None, timezone: str = "localtime"
) -> tuple[list, Callable]:
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
    tuple[list, Callable]
        A tuple containing a list of indices of columns, and a Callable to which the
        columns have to be passed to obtain a uts timestamp.

    """
    if timezone == "localtime":
        tz = tzlocal.get_localzone()
    else:
        tz = zoneinfo.ZoneInfo(timezone)
    if spec is not None:
        if "uts" in spec:
            return [spec["uts"].get("index", None)], float
        if "timestamp" in spec:
            if "format" in spec["timestamp"]:

                def retfunc(value):
                    dt = datetime.datetime.strptime(value, spec["timestamp"]["format"])
                    local_tz = tz if dt.tzinfo is None else dt.tzinfo
                    local_dt = dt.replace(tzinfo=local_tz)
                    utc_dt = local_dt.astimezone(datetime.timezone.utc)
                    return utc_dt.timestamp()

                return [spec["timestamp"].get("index", None)], retfunc
            else:
                logging.debug(
                    "dateutils: Assuming specified column containing the timestamp is in ISO 8601 format"
                )

                def retfunc(value):
                    dt = dateutil.parser.parse(value)
                    local_tz = tz if dt.tzinfo is None else dt.tzinfo
                    local_dt = dt.replace(tzinfo=local_tz)
                    utc_dt = local_dt.astimezone(datetime.timezone.utc)
                    return utc_dt.timestamp()

                return [spec["timestamp"].get("index", None)], retfunc
        if "date" in spec or "time" in spec:
            specdict = {
                "date": datetime.datetime.fromtimestamp(0, tz=tz).timestamp,
                "time": datetime.datetime.fromtimestamp(0, tz=tz).timestamp,
            }
            cols = [None, None]
            if "date" in spec:
                if "format" in spec["date"]:

                    def datefn(value):
                        dt = datetime.datetime.strptime(value, spec["date"]["format"])
                        local_tz = tz if dt.tzinfo is None else dt.tzinfo
                        local_dt = dt.replace(tzinfo=local_tz)
                        utc_dt = local_dt.astimezone(datetime.timezone.utc)
                        return utc_dt.timestamp()

                    cols[0] = spec["date"].get("index", None)
                else:
                    logging.debug(
                        "dateutils: Assuming specified column containing the date is in ISO 8601 format"
                    )

                    def datefn(value):
                        dt = dateutil.parser.parse(value)
                        local_tz = tz if dt.tzinfo is None else dt.tzinfo
                        local_dt = dt.replace(tzinfo=local_tz)
                        utc_dt = local_dt.astimezone(datetime.timezone.utc)
                        return utc_dt.timestamp()

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
                return [cols[1]], specdict["time"]
            elif cols[1] is None:
                return [cols[0]], specdict["date"]
            else:

                def retfn(date, time):
                    return specdict["date"](date) + specdict["time"](time)

                return cols, retfn
    elif "uts" in headers:
        logging.info(
            "dateutils: No timestamp spec provided, assuming column 'uts' is a valid unix timestamp"
        )
        return [headers.index("uts")], float
    elif "timestamp" in headers:
        logging.info(
            "dateutils: No timestamp spec provided, assuming column 'timestamp' is a valid ISO 8601 timestamp"
        )

        def retfunc(value):
            dt = dateutil.parser.parse(value)
            local_tz = tz if dt.tzinfo is None else dt.tzinfo
            local_dt = dt.replace(tzinfo=local_tz)
            utc_dt = local_dt.astimezone(datetime.timezone.utc)
            return utc_dt.timestamp()

        return [headers.index("timestamp")], retfunc
    else:
        assert False, "dateutils: A valid timestamp could not be deduced."


def date_from_str(datestr: str) -> Union[float, None]:
    bn = os.path.basename(datestr)
    for f, l in [["%Y%m%d", 8], ["%Y-%m-%d", 10]]:
        _, df = infer_timestamp_from([], {"date": {"index": 0, "format": f}})
        try:
            day = df(bn[:l])
            return day
        except ValueError:
            pass
    logging.warning(f"dateutils: was not possible to interpret {datestr} as date")
    return None
