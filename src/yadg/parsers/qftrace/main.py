from scipy.signal import find_peaks
import numpy as np
from pydantic import BaseModel
from . import labviewcsv


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "timezone",
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
    """
    VNA reflection trace parser.

    This parser processes a VNA log file, containing the complex reflection coefficient
    data as a function of frequency (:math:`\\Gamma(f)`). This data is automatically
    worked up to produce the quality factor :math:`Q_0` and the central frequency
    :math:`f_0` of all peaks found in each trace; hence the name ``qftrace``.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.QFTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. The currently only
        supported tracetype ("labview.csv") does not return full date.
    """
    if parameters.filetype == "labview.csv":
        data, meta = labviewcsv.process(fn, encoding, timezone)
        fulldate = False
    
    return data, meta, fulldate
