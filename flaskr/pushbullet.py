# -*- coding: utf-8 -*-

"""
    G2 Server
    Copyright (C) 2020 J0rdyZ65

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import requests

from flask import current_app


def redirect_url():
    return ('https://www.pushbullet.com/authorize' +
            '?client_id=' + current_app.config['PUSHBULLET_G2_CLIENT_ID'] +
            '&redirect_uri=' + current_app.config['G2_SERVER_AUTH_COMPLETE_URL'] +
            '&response_type=code')


def author(args):
    return _pb_api_oauth2_token(args['code'])['access_token']


def _pb_api_oauth2_token(code):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        'client_id': current_app.config['PUSHBULLET_G2_CLIENT_ID'],
        'client_secret': current_app.config['PUSHBULLET_G2_CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code',
    }

    # (notice) pushbullet API expects json encoded parameters
    res = requests.post('https://api.pushbullet.com/oauth2/token', json=data, headers=headers)
    res.raise_for_status()
    return res.json()
