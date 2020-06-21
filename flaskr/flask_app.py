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

import os
import time

from flask import Flask, request

import db


app = Flask('g2server', instance_relative_config=True) #pylint: disable=C0103
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'g2server.db'),
)
app.teardown_appcontext(db.close_db)
app.logger.debug('app.instance_path: {}', app.instance_path)


@app.route('/key')
def key():
    client_ip = request.access_route[0]
    code = request.args.get('code')
    if not code:
        return ('NOT FOUND', 404)
    dbc = db.get_db()
    with dbc as dbt:
        dbt.execute('REPLACE INTO codes VALUES (?, ?, ?, ?)', (client_ip, code, '', time.time()))
    return 'Request from {} with code {}'.format(client_ip, code)


@app.route('/auth')
def auth():
    return 'Once completed, this site should redirect you somewhere else!'
