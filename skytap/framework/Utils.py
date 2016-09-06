"""Some basic utility functions that help out with the Skytap API."""

from datetime import datetime, timedelta, tzinfo, date, time
import json
import logging
from collections import namedtuple
from skytap.framework.timezones import TIMEZONES, REV_TIMEZONES

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


DateString = namedtuple('DateString', ('date_string', 'tz_string'))

def convert_date_for_json(dt, return_as=None, ret_as_tz=None, ret_tz=True):
    """
    :param date_obj:
    :type date_obj:
    :param return_as: 'date'|'time'|'datetime'|<dt_format_str>
        - note will raise ValueError if 'return_as' does not match the dt object
            (i.e., if a time() object is passed and return_as is set to 'date'.)
        - if None, will return the same type as dt object,
    :type return_as: str
    :param ret_tz: what timezone to use for dates saved to ST, can be:
        - Any of the valid options for the SkytapTimezone object.
        - 'Default': will use the tz in the dt object if present, otherwise 'UTC'.
        - None (in which case, UTC is passed.
    :param inc_tz: indicates if the tz value should be appended to the return dt string (defaults to True)
    :return: DateString

    :rtype:
    """
    tz_obj = None

    if return_as is None:
        return_as = dt.__class__.__name__
    if return_as == 'date':
        format_str = '%Y/%m/%d'
    elif return_as == 'time':
        format_str = '%H:%M'
    elif return_as == 'datetime':
        format_str = '%Y/%m/%d %H:%M:%S'
    else:
        format_str = return_as

    if return_as == 'date' and (ret_as_tz is not None or ret_tz):
        raise ValueError('Timezone return is not possible with date only objects')

    if ret_as_tz is None:
        tz_obj = SkytapTimeZone('UTC')
    elif isinstance(ret_as_tz, str) and ret_as_tz.lower() == 'default':
        if dt.tzinfo is not None:
            tz_obj = dt.tzinfo
        else:
            tz_obj = SkytapTimeZone('UTC')
    else:
        tz_obj = SkytapTimeZone(ret_as_tz)

    if ret_tz:
        format_str += ' %z'

    if tz_obj is None or return_as == 'date':
        tz_str = ''
    else:
        tz_str = tz_obj.tzname()

    if isinstance(dt, datetime):
        if dt.tzinfo is not None:
            tmp_dt = dt.astimezone(tz_obj)
        else:
            if ret_tz:
                tmp_dt = dt.replace(tzinfo=tz_obj)
            else:
                tmp_dt = dt
        tmp_ret = tmp_dt.strftime(format_str)
        return DateString(tmp_ret, tz_str)

    if isinstance(dt, time):
        tmp_dt = datetime(2000, 1, 1)
        tmp_dt = datetime.combine(tmp_dt, dt)
        if tmp_dt.tzinfo is not None:
            print('found tz in time, tz= %s' % tmp_dt.tzinfo.tzname())
            tmp_dt = tmp_dt.astimezone(tz_obj)
            print('found tz in time, tz= %s' % tmp_dt.tzinfo.tzname())
        else:
            tmp_dt = tmp_dt.replace(tzinfo=tz_obj)

        tmp_time = tmp_dt.timetz()

        print('format string = %s' % format_str)
        print(tmp_time.strftime(format_str))
        tmp_ret = tmp_time.strftime(format_str)
        return DateString(tmp_ret, tz_str)

    else:
        tmp_ret = dt.strftime(format_str)
        return DateString(tmp_ret, tz_str)


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
        elif ':' in pdo and pdo[0] not in '+-':
            short_time_str = pdo
        else:
            short_tz_str = pdo
            has_tz_info = True

    if short_date_str is not None and short_time_str is not None:
        short_dt_str = '%s %s' % (short_date_str, short_time_str)
        naive_ret = datetime.strptime(short_dt_str, '%Y/%m/%d %H:%M:%S')

    elif short_time_str is not None and short_date_str is None:
        # date only
        if short_time_str.count(':') == 1:
            naive_ret = datetime.strptime(short_time_str, '%H:%M').time()
        else:
            naive_ret = datetime.strptime(short_time_str, '%H:%M:%S').time()

    if naive_ret is not None:
        if has_tz_info:
            if short_tz_str is not None:
                tz_str = short_tz_str
            dt = naive_ret.replace(tzinfo=SkytapTimeZone(tz_str))
            return dt
        else:
            return naive_ret
    else:
        return datetime.strptime(short_date_str, '%Y/%m/%d').date()

class SkytapTimeZone(tzinfo):
    """
    handles various timezone offset methods used in ST
    Fixed offset in minutes: `time = utc_time + utc_offset`.

    This will also return an approximate skytap timezone name based on the timezone offset.

    This should be able to replace the FixedOffset below, but it will return a different __name response... so I did
    not want to just replace it in case there the __name was used somewhere.

    """

    def __init__(self, offset=None):
        """
        :param offset:
            can be any one of:
                - <int>: number of seconds of offset
                - '-0000': string offset
                - '-0:00': alternate format string offset
                - '<timezone name>': string name of timezone from Skytap list.
                - tzone_obj: timezone object.
        """
        self.__name = None

        if isinstance(offset, str):
            tmp_init_offset = offset
            tmp_name = None
            if offset in TIMEZONES:
                tmp_name = offset
                offset = TIMEZONES[offset]

            elif offset[0] in ('-', '+') and ':' in offset and len(offset) == 6:
                offset = offset.replace(':', '')

            if offset[0] not in ('-', '+') or len(offset) != 5:
                raise ValueError('Timezone "%s" cannot be determined' % tmp_init_offset)

            if tmp_name is None:
                tmp_name = REV_TIMEZONES.get(offset, offset)

            self.__name = tmp_name

            offset_num = int(offset[-4:-2]) * 60 + int(offset[-2:])

            if offset[0] == "-":
                offset_num = -offset_num
            offset = offset_num

        elif isinstance(offset, tzinfo):
            offset = offset.utcoffset().minutes
            try:
                self.__name = offset.tzname()
                if self.__name not in TIMEZONES:
                    self.__name = None
            except:
                pass

        elif offset is None:
            offset = 0
            self.__name = 'UTC'

        """Given offset, built timezone info."""
        self.__offset = timedelta(minutes=offset)
        hours, minutes = divmod(offset, 60)
        self.offset_str = '%+03d%02d' % (hours, minutes)
        # NOTE: the last part is to remind about deprecated POSIX GMT+h
        #  timezones that have the opposite sign in the name;
        #  the corresponding numeric value is not used e.g., no minutes
        if self.__name is None:
            self.__name = REV_TIMEZONES.get(self.offset_str, self.offset_str)

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
        return 'SkytapTimeZone(%d)' % (total_seconds / 60)


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
