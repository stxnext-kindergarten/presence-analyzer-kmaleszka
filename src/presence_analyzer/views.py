# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import locale
from flask import redirect, render_template

from presence_analyzer.main import app
from presence_analyzer.utils import (jsonify, get_data, mean, group_by_weekday,
                                     group_by_start_end, get_users_from_xml)

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday')


@app.route('/mean_time_weekday')
def mean_time_weekday_page():
    """
    Renders mean time page.
    """
    return render_template('mean_time_weekday.html')


@app.route('/presence_weekday')
def presence_weekday_page():
    """
    Renders weekday page.
    """
    return render_template('presence_weekday.html')


@app.route('/presence_start_end')
def presence_start_end_page():
    """
    Renders start-end presences page.
    """
    return render_template('presence_start_end.html')


@app.route('/api/v2/users', methods=['GET'])
@jsonify
def users_view_v2():
    """
    Users listing for dropdown, new api.
    """

    data = get_users_from_xml()
    result = [{'user_id': i, 'name': data[i]['name'],
              'avatar_url': data[i]['avatar_url']}
              for i in data.keys()]
    result.sort(key=lambda user: user['name'], cmp=locale.strcoll)
    return result


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns presence average time.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_start_end(data[user_id])
    result = []

    for (weekday, presence_dict) in weekdays.items():
        start = mean(presence_dict['start_list'])
        end = mean(presence_dict['end_list'])
        result.append([calendar.day_abbr[weekday], start, end])
    return result
