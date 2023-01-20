from typing import Tuple, Union, Optional
from zoneinfo import ZoneInfo
from abc import ABC, abstractmethod
from pathlib import Path
import tzlocal
import locale as loc


class StepDefaults:
    timezone: ZoneInfo
    locale: Union[Tuple[str, str], str]
    encoding: str

    def __init__(self, defaults=None):
        self.timezone = ZoneInfo(tzlocal.get_localzone_name())
        self.locale = loc.getlocale(loc.LC_NUMERIC)
        if self.locale == (None, None):
            self.locale = loc.getlocale()
        self.encoding = "UTF-8"

        if defaults is not None:
            if defaults.timezone is not None and defaults.timezone != "localtime":
                self.timezone = ZoneInfo(defaults.timezone)
            if defaults.locale is not None:
                self.locale = loc.normalize(defaults.locale)
            if defaults.encoding is not None:
                self.encoding = defaults.encoding

    def __repr__(self):
        return f"StepDefaults(timezone='{self.timezone}', locale={self.locale}, encoding='{self.encoding}')"


class Extractor:
    timezone: ZoneInfo
    locale: Union[Tuple[str, str], str]
    encoding: str

    def __init__(
        self,
        defaults: StepDefaults,
        timezone: Optional[str] = None,
        locale: Optional[str] = None,
        encoding: Optional[str] = None,
    ):
        self.timezone = defaults.timezone
        if timezone is not None:
            self.timezone = ZoneInfo(timezone)

        self.locale = defaults.locale
        if locale is not None:
            self.locale = loc.normalize(locale)

        self.encoding = defaults.encoding
        if encoding is not None:
            self.encoding = encoding

    # @abstractmethod
    # def extract(self, path: Path) -> dict:
    #    pass
