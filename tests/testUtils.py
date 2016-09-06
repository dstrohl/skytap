import json
import nose
import sys
from datetime import datetime, timedelta, tzinfo, date, time
from collections import namedtuple

sys.path.append('..')
import skytap.framework.Utils as Utils  # noqa


def test_date_configs():
    gmt_tz = Utils.FixedOffset(0)
    pst_tz = Utils.FixedOffset(-480)

    dt_tz_check = datetime(year=2015, month=9, day=8, hour=0, minute=26, second=48, tzinfo=pst_tz)
    dt_tz_check2 = datetime(year=2015, month=9, day=8, hour=0, minute=26, second=48, tzinfo=gmt_tz)
    dt_check = datetime(year=2015, month=9, day=8, hour=0, minute=26, second=48)

    time_tz_check = time(hour=0, minute=26, second=48, tzinfo=pst_tz)
    time_check = time(hour=0, minute=26, second=48)
    time_tz_check2 = time(hour=0, minute=26, tzinfo=pst_tz)

    date_check = date(year=2015, month=9, day=8)

    assert Utils.convert_date('2015/09/08 00:26:48 -0800') == dt_tz_check

    assert Utils.convert_date('2015/09/08 00:26:48', '-0800') == dt_tz_check
    assert Utils.convert_date('2015/09/08 00:26:48', 'Pacific Time (US & Canada)') == dt_tz_check

    assert Utils.convert_date('2015/09/08 00:26:48 -0000') == dt_tz_check2

    assert Utils.convert_date('2015/09/08 00:26:48') == dt_check

    assert Utils.convert_date('00:26:48 -0800') == time_tz_check
    assert Utils.convert_date('00:26:48', '-0800') == time_tz_check
    assert Utils.convert_date('00:26:48', 'Pacific Time (US & Canada)') == time_tz_check

    assert Utils.convert_date('00:26:48') == time_check

    assert Utils.convert_date('00:26 -0800') == time_tz_check2
    assert Utils.convert_date('00:26', '-0800') == time_tz_check2
    assert Utils.convert_date('00:26', 'Pacific Time (US & Canada)') == time_tz_check2

    assert Utils.convert_date('2015/09/08') == date_check


def test_st_tz_obj():
    tz = Utils.SkytapTimeZone(1)
    assert tz.utcoffset().seconds == 60


def test_st_tz_as_tz_str():
    tz = Utils.SkytapTimeZone('+0001')
    assert tz.utcoffset().seconds == 60


def test_st_tz_as_tz_str_2():
    tz = Utils.SkytapTimeZone('+01:00')
    print(tz.utcoffset().seconds)
    assert tz.utcoffset().seconds == 3600


def test_st_tz_as_tz_str_3():
    tz = Utils.SkytapTimeZone('+0100')
    assert tz.utcoffset().seconds == 3600


def test_st_tz_as_tz_name():
    tz = Utils.SkytapTimeZone('UTC')
    assert tz.utcoffset().seconds == 0


def test_st_tz_as_tz_name2():
    tz = Utils.SkytapTimeZone()
    assert tz.utcoffset().seconds == 0
    assert tz.tzname() == 'UTC'

def test_st_tz_as_tz_name3():
    tz = Utils.SkytapTimeZone('Amsterdam')
    print(tz.utcoffset().seconds)
    assert tz.utcoffset().seconds == 3600
    assert tz.tzname() == 'Amsterdam'


def test_st_tz_as_tz_name4():
    tz = Utils.SkytapTimeZone('Azores')
    print(tz.utcoffset().seconds)
    assert tz.utcoffset().seconds == 82800
    assert tz.tzname() == 'Azores'


DT2JTestSet = namedtuple('DT2JTestSet', ('run', 'kwargs', 'dt_string', 'tz_string'))
DT2JTestKwargs = namedtuple('DT2JTestKwargs', ('dt', 'return_as', 'ret_as_tz', 'ret_tz'))

DT2JTests = [
    DT2JTestSet(1, DT2JTestKwargs('dt_tz_check_utc', None, None, True), '2015/02/01 12:30:30 +0000', 'UTC'),
    DT2JTestSet(2, DT2JTestKwargs('dt_tz_check_m1', None, None, True), '2015/02/01 12:30:30 +0000', 'UTC'),
    DT2JTestSet(3, DT2JTestKwargs('dt_tz_check_p1', None, None, True), '2015/02/01 12:30:30 +0000', 'UTC'),
    DT2JTestSet(4, DT2JTestKwargs('dt_check_no_tz', None, None, True), '2015/02/01 12:30:30 +0000', 'UTC'),
    DT2JTestSet(5, DT2JTestKwargs('time_tz_check_utc', None, None, True), '12:30 +0000', 'UTC'),
    DT2JTestSet(6, DT2JTestKwargs('time_tz_check_m1', None, None, True), '12:30 +0000', 'UTC'),
    DT2JTestSet(7, DT2JTestKwargs('time_tz_check_p1', None, None, True), '12:30 +0000', 'UTC'),
    DT2JTestSet(8, DT2JTestKwargs('time_check_no_tz', None, None, True), '15:45 +0000', 'UTC'),
    DT2JTestSet(9, DT2JTestKwargs('date_check', None, None, False), '2015/02/03', ''),
    DT2JTestSet(10, DT2JTestKwargs('dt_tz_check_utc', 'date', None, False), '2015/02/01', ''),
    DT2JTestSet(11, DT2JTestKwargs('dt_tz_check_m1', 'datetime', None, True), '2015/02/01 12:30:30 +0000', 'UTC'),
    DT2JTestSet(12, DT2JTestKwargs('dt_tz_check_p1', 'time', None, True), '12:30 +0000', 'UTC'),
    DT2JTestSet(13, DT2JTestKwargs('dt_check_no_tz', '%H:%MT%Y/%d', None, True), '12:30T2015/01 +0000', 'UTC'),
    DT2JTestSet(14, DT2JTestKwargs('time_tz_check_m1', 'time', None, True), '12:30 +0000', 'UTC'),
    DT2JTestSet(15, DT2JTestKwargs('time_check_no_tz', '%H:%S', None, True), '15:45 +0000', 'UTC'),
    DT2JTestSet(16, DT2JTestKwargs('date_check', 'date', None, False), '2015/02/03', ''),
    DT2JTestSet(17, DT2JTestKwargs('dt_tz_check_utc', None, 'Azores', True), '2015/02/01 11:30:30 -0100', 'Azores'),
    DT2JTestSet(18, DT2JTestKwargs('dt_tz_check_m1', None, 'default', True), '2015/02/01 11:30:30 -0100', 'Azores'),
    DT2JTestSet(19, DT2JTestKwargs('dt_tz_check_p1', None, 'Amsterdam', True), '2015/02/01 13:30:30 +0100', 'Amsterdam'),
    DT2JTestSet(20, DT2JTestKwargs('dt_check_no_tz', None, 'Azores', True), '2015/02/01 12:30:30 -0100', 'Azores'),
    DT2JTestSet(21, DT2JTestKwargs('time_tz_check_utc', None, 60, True), '13:30 +0100', 'Paris'),
    DT2JTestSet(22, DT2JTestKwargs('time_tz_check_m1', None, '-0300', True), '09:30 -0300', 'Buenos Aires'),
    DT2JTestSet(23, DT2JTestKwargs('time_tz_check_p1', None, None, True), '12:30 +0000', 'UTC'),
    DT2JTestSet(24, DT2JTestKwargs('dt_tz_check_utc', None, 'Amsterdam', True), '2015/02/01 13:30:30 +0100', 'Amsterdam'),
    DT2JTestSet(25, DT2JTestKwargs('dt_tz_check_m1', None, 'Azores', False), '2015/02/01 11:30:30', 'Azores'),
    DT2JTestSet(26, DT2JTestKwargs('dt_tz_check_p1', None, None, True), '2015/02/01 12:30:30 +0000', 'UTC'),
    DT2JTestSet(27, DT2JTestKwargs('dt_check_no_tz', None, 'Amsterdam', False), '2015/02/01 12:30:30', 'Amsterdam'),
    DT2JTestSet(28, DT2JTestKwargs('time_tz_check_utc', None, 'Azores', True), '11:30 -0100', 'Azores'),
    DT2JTestSet(29, DT2JTestKwargs('time_tz_check_m1', None, 'UTC', False), '12:30', 'UTC'),
    DT2JTestSet(30, DT2JTestKwargs('time_tz_check_p1', None, None, True), '12:30 +0000', 'UTC'),
    DT2JTestSet(31, DT2JTestKwargs('time_check_no_tz', None, 'Azores', False), '15:45', 'Azores'),
    DT2JTestSet(32, DT2JTestKwargs('date_check', None, None, False), '2015/02/03', ''),]

def test_dt_to_json():

    gmt_tz = Utils.SkytapTimeZone()
    gmt_p1_tz = Utils.SkytapTimeZone('Amsterdam')
    gmt_m1_tz = Utils.SkytapTimeZone('Azores')

    test_dates = dict(
        dt_tz_check_utc=datetime(year=2015, month=2, day=1, hour=12, minute=30, second=30, tzinfo=gmt_tz),
        dt_tz_check_m1=datetime(year=2015, month=2, day=1, hour=11, minute=30, second=30, tzinfo=gmt_m1_tz),
        dt_tz_check_p1=datetime(year=2015, month=2, day=1, hour=13, minute=30, second=30, tzinfo=gmt_p1_tz),

        dt_check_no_tz=datetime(year=2015, month=2, day=1, hour=12, minute=30, second=30),

        time_tz_check_utc=time(hour=12, minute=30, second=30, tzinfo=gmt_tz),
        time_tz_check_m1=time(hour=11, minute=30, second=30, tzinfo=gmt_m1_tz),
        time_tz_check_p1=time(hour=13, minute=30, second=30, tzinfo=gmt_p1_tz),

        time_check_no_tz=time(hour=15, minute=45, second=45),

        date_check=date(year=2015, month=2, day=3))

    for test in DT2JTests:
        yield check_dt2j, test, test_dates
        # test_kwargs = test.kwargs._asdict()
        # test_kwargs['dt'] = test_dates[test_kwargs['dt']]


        # test_ret = Utils.convert_date_for_json(**test_kwargs)

        # print('Run: %s, expected: "%s", returned: "%s"' %(test.run, test_ret.date_string, test.dt_string))
        # assert test_ret.date_string == test.dt_string
        # print('Run: %s, expected: "%s", returned: "%s"' % (test.run, test_ret.tz_string, test.tz_string))
        # assert test_ret.tz_string == test.tz_string

        # yield check_strings, test.run, test.dt_string, test_ret.date_string
        # yield check_strings, test.run, test.tz_string, test_ret.tz_string


def check_dt2j(test, test_dates):
    test_kwargs = test.kwargs._asdict()
    test_kwargs['dt'] = test_dates[test_kwargs['dt']]

    test_ret = Utils.convert_date_for_json(**test_kwargs)

    print('Run: %s, returned: "%s", expected: "%s"' % (test.run, test_ret.date_string, test.dt_string))
    assert test_ret.date_string == test.dt_string
    print('Run: %s, returned: "%s", expected: "%s"' % (test.run, test_ret.tz_string, test.tz_string))
    assert test_ret.tz_string == test.tz_string



def check_strings(name, expected_string, returned_string):
    if expected_string == returned_string:
        assert expected_string == returned_string
    else:
        print('Run: %s' % name)
        print('    Expected: %s' % expected_string)
        print('    Returned: %s' % returned_string)
