import json
import nose
import sys
from datetime import datetime, timedelta, tzinfo, date, time

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
