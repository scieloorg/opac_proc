# coding: utf-8
from datetime import datetime
from unittest import main, TestCase

from dateutil.parser import parse

from opac_proc.source_sync.utils import parse_date_str_to_datetime_obj


class TestSourceSyncUtils(TestCase):

    def test_parse_date_str_to_datetime_obj_YYYYMMDD_ok(self):
        test_dates = ('2017-05-27', '2005-12-01', '2010-01-31')
        for date in test_dates:
            expected = datetime.strptime(date, '%Y-%m-%d')
            result = parse_date_str_to_datetime_obj(date)
            self.assertEqual(result.year, expected.year)
            self.assertEqual(result.month, expected.month)
            self.assertEqual(result.day, expected.day)
            self.assertEqual(result.hour, expected.hour)
            self.assertEqual(result.minute, expected.minute)
            self.assertEqual(result.second, expected.second)

    def test_parse_date_str_to_datetime_obj_RFC2822_full_datetime_ok(self):
        test_dates = ('Sat, 27 May 2017 16:01:27 -0300',
                      'Thu, 01 Dec 2005 08:34:03 +0500',
                      'Sun, 31 Jan 2010 23:59:59 -0000')
        for date in test_dates:
            expected = parse(date)
            result = parse_date_str_to_datetime_obj(date)
            self.assertEqual(result.year, expected.year)
            self.assertEqual(result.month, expected.month)
            self.assertEqual(result.day, expected.day)
            self.assertEqual(result.hour, expected.hour)
            self.assertEqual(result.minute, expected.minute)
            self.assertEqual(result.second, expected.second)
            self.assertEqual(result.weekday(), expected.weekday())
            self.assertEqual(result.tzinfo, expected.tzinfo)


if __name__ == '__main__':
    main()
