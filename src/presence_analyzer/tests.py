# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()
        self.weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_mean_time_weekday(self):
        """
        Test mean time weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        for item in zip(data, self.weekdays):
            weekday_header = item[0][0]
            weekday_name = item[1]
            self.assertEqual(weekday_header, weekday_name)

    def test_api_presence_weekday(self):
        """
        Test presence weekday.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        header = data[0]
        self.assertListEqual(header, ['Weekday', 'Presence (s)'])
        for item in zip(data[1:], self.weekdays):
            weekday_header = item[0][0]
            weekday_name = item[1]
            self.assertEqual(weekday_header, weekday_name)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """
        Test grouping user time by weekday.
        """
        data = utils.get_data()
        for user in data.itervalues():
            current_user = utils.group_by_weekday(user)
            self.assertIsInstance(current_user, dict)
            self.assertItemsEqual(current_user.keys(), [x for x in range(7)])
            for item in current_user.itervalues():
                self.assertIsInstance(item, list)
        sample_user = utils.group_by_weekday(data[10])
        self.assertItemsEqual(sample_user[1], [30047])

    def test_seconds_since_midnight(self):
        """
        Test amount of second since midnight.
        """
        sample_time = datetime.time(00, 00, 20)
        result = utils.seconds_since_midnight(sample_time)
        self.assertEqual(result, 20)

    def test_interval(self):
        """
        Test interval function.
        """
        start = datetime.time(9, 40, 00)
        end = datetime.time(10, 20, 00)
        result = utils.interval(start, end)
        self.assertEqual(result, 2400)

    def test_mean(self):
        """
        Test arithmetic mean.
        """
        result = utils.mean([1, 2, 3, 4])
        self.assertEqual(result, 2.5)
        result = utils.mean([])
        self.assertEqual(result, 0)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
