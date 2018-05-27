import re
from datetime import datetime, timedelta

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
DURATION_REGEX = re.compile(r'(\d+):(\d\d)')


def strptime(txt: str):
    return datetime.strptime(txt, DATETIME_FORMAT)


def strftime(dt: datetime):
    return dt.strftime(DATETIME_FORMAT)


class Duration(int):
    def __new__(cls, txt):
        match = DURATION_REGEX.match(txt)
        if match is None:
            raise ValueError('No valid duration text')
        minutes = int(match.group(1))*60 + int(match.group(2))
        self = int.__new__(cls, minutes)
        self.minutes = minutes % 60
        self.hours = minutes // 60
        return self


class Delay(int):
    def __new__(cls, minutes, friendly_str=None):
        self = int.__new__(cls, cls.parse_delay(minutes))
        if friendly_str is None:
            if minutes:
                self.friendly = '+{} min'.format(minutes)
            else:
                self.friendly = ''
        else:
            self.friendly = friendly_str
        return self

    def __str__(self):
        return self.friendly.__str__()

    def __format__(self, format_spec):
        """
            A format spec with type 's' returns the friendly string,
            any other format spec returns just the number of minutes
        """
        if format_spec[-1] == 's':
            return self.friendly.__format__(format_spec)
        return int.__format__(self, format_spec)

    @staticmethod
    def parse_delay(txt: str):
        try:
            return int(txt)
        except ValueError:
            try:
                return int(re.match(r'PT(\d+)M', txt).group(1))
            except ValueError:
                return None
