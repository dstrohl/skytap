"""Some basic utility functions that help out with the Skytap API."""

from datetime import datetime, timedelta, tzinfo, date, time
import json
import logging
from skytap.framework.timezones import TIMEZONES

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Set up the logging system:

logging.getLogger(__name__).addHandler(NullHandler())
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')  # noqa
handler.setFormatter(formatter)
logger.addHandler(handler)


def debug(msg):
    logger.debug(msg)


def warning(msg):
    logger.warning(msg)


def info(msg):
    logger.info(msg)


def critical(msg):
    logger.critical(msg)


def log(level, msg):
    logger.log(level, msg)


def log_level(level=None):
    if level is not None:
        logger.setLevel(level)
    return logger.getEffectiveLevel()


def error(err):
    """Convert an error message into JSON."""
    logger.error(err)
    return json.dumps({"error": err})


def convert_date(date_str, tz_str=None):

    """Convert a Skytap date string to a datetime object.

    will handle the following transformations:
        will return Datetime objects:
          - '2015/09/08 00:26:48 -0800'
          - '2015/09/08 00:26:48', tz_str='-0800'
          - '2015/09/08 00:26:48', tz_str='PST'
          - '2015/09/08 00:26:48', tz_str='Pacific Standard Time'

        will return Time objects:
          - '00:26:48 -0800'
          - '00:26:48', tz_str='-0800'
          - '00:26:48', tz_str='PST'
          - '00:26', tz_str='PST'
          - '00:26:48', tz_str='Pacific Standard Time'

        will return Date objects:
          - '2015/09/08'
            (note, this ignores any timezone information)

        if no tz info is found, a naive object is returned.

    Sample from Skytap: 2015/09/08 00:26:48 -0800
    """
    parsed_date_obj = date_str.split(' ')
    short_date_str = None
    short_time_str = None
    short_tz_str = None
    has_tz_info = tz_str is not None
    naive_ret = None
    for pdo in parsed_date_obj:
        if '/' in pdo:
            short_date_str = pdo
        elif ':' in pdo:
            short_time_str = pdo
        else:
            short_tz_str = pdo
            has_tz_info = True

    if short_date_str is not None and short_time_str is not None:
        short_dt_str = '%s %s' % (short_date_str, short_time_str)
        naive_ret = datetime.strptime(short_dt_str, '%Y/%m/%d %H:%M:%S')

    elif short_time_str is not None and short_date_str is None:
        # date only
        naive_ret = time(*':'.split(short_time_str))

    if naive_ret is not None:
        if has_tz_info:
            if short_tz_str is not None:
                offset_str = short_tz_str
            else:
                offset_str = TIMEZONES.get(tz_str, '-00:00')

            offset = int(offset_str[-4:-2]) * 60 + int(offset_str[-2:])
            if offset_str[0] == "-":
                offset = -offset
            dt = naive_ret.replace(tzinfo=FixedOffset(offset))
            return dt
        else:
            return naive_ret
    else:
        naive_ret = date(*'/'.split(short_date_str))
        return


class FixedOffset(tzinfo):

    """Fixed offset in minutes: `time = utc_time + utc_offset`."""

    def __init__(self, offset):
        """Given offset, built timezone info."""
        self.__offset = timedelta(minutes=offset)
        hours, minutes = divmod(offset, 60)
        # NOTE: the last part is to remind about deprecated POSIX GMT+h
        #  timezones that have the opposite sign in the name;
        #  the corresponding numeric value is not used e.g., no minutes
        self.__name = '<%+03d%02d>%+d' % (hours, minutes, -hours)

    def utcoffset(self, dt=None):
        """Return UTC offset."""
        return self.__offset

    def tzname(self, dt=None):
        """Return timezone name."""
        return self.__name

    def dst(self, dt=None):
        """Ignore daylight savings time."""
        return timedelta(0)

    def __repr__(self):
        """String representation of the offset."""
        total_seconds = (self.utcoffset().microseconds + 0.0 +
                         (self.utcoffset().seconds + self.utcoffset().days *
                         24 * 3600) * 10 ** 6) / 10 ** 6
        return 'FixedOffset(%d)' % (total_seconds / 60)
