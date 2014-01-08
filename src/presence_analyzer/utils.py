# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
from json import dumps
from functools import wraps
from datetime import datetime
import time
import threading

from flask import Response

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

user_data_cache = None
cache_last_update = 0


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


def cache(time_in_sec):
    """
    Create cache decorator for get_data function.
    """
    def wrap(function):
        update_diff = time_in_sec
        cache_last_update = time.time()
        lock = threading.Lock()

        def inner(*args, **kwargs):
            lock.acquire()

            global user_data_cache, cache_last_update

            if not user_data_cache:
                user_data_cache = function()

            current_time = time.time()
            diff = current_time - cache_last_update

            if diff > update_diff:
                cache_last_update = time.time()
                user_data_cache = function()
            lock.release()
            return user_data_cache
        return inner
    return wrap


@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def group_by_start_end(user):
    """
    Groups presence entries by weekday and start/end time.

    It creates dictionary like this:

    {
     0: {'start_list':[30100,  ...], 'end_list': [20130, ...]},
     ...
     6: {'start_list': [12301, ...], 'end_list': [12312, ...]}
    }
    """
    result = {i: {'start_list': [], 'end_list': []} for i in range(7)}
    for date in user:
        weekday = datetime.weekday(date)
        start = seconds_since_midnight(user[date]['start'])
        end = seconds_since_midnight(user[date]['end'])
        result[weekday]['start_list'].append(start)
        result[weekday]['end_list'].append(end)
    return result
