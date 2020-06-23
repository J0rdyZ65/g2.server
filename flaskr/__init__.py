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
import logging
from six.moves import urllib

from flask import Flask, request, redirect, url_for, abort

from . import db


app = Flask('g2server', static_folder='g2.server/static', instance_relative_config=True) #pylint: disable=C0103
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'g2server.sqlite'),
)
app.teardown_appcontext(db.close_db)
app.logger.setLevel(logging.DEBUG)


@app.route('/icon.png')
def icon():
    return redirect(url_for('static', filename='icon.png'))


@app.route('/code', methods=['POST'])
def code():
    """Route for the client requesting the authentication on behalf of the user."""

    client_ip = request.access_route[0]
    client_name = request.form['client_name']
    client_hash = request.form['client_hash']
    redirect_url = request.form['redirect_url']

    row = db.get_by_client(client_ip, client_hash, client_name, redirect_url)
    res = {
        # url that the client present to the user
        'url': 'https://tinyurl.com/g2auth?c={}]'.format(row['g2_server_client_id']),
        # time in secs that the client has to wait before posting a new request
        'interval': 5,
        'expire_in': db.ENTRY_TIMEOUT,
    }
    if row['service_code']:
        res['service_code'] = row['service_code']
    return res


@app.route('/auth')
def auth():
    """Route for the user looking to authenticate himself with the 3P service"""

    client_ip = request.access_route[0]

    try:
        g2_server_client_id = request.args.get('c')
        row = db.get_by_user(client_ip, g2_server_client_id)
        # Display this message for a while before redirecting (need to use browser refresh?)
        # 'You are going to be redirect to {} for authentication'.format(domain(row['redirect_url']))
        return redirect(row['redirect_url'])
    except db.MissingEntry:
        app.logger.debug('client IP %s does not have any active authentication session', client_ip)
        abort(404)
    except db.TooManyMatches:
    	# (fixme) Intl
        return 'You should have given an url ending with c=N, please use the full url', 404


@app.route('/auth_complete')
def auth_complete():
    """Route for the user after successfull authentication with the 3P service"""

    client_ip = request.access_route[0]

    try:
        g2_server_client_id = request.args.get('c')
        row = db.get_by_user(client_ip, g2_server_client_id)
        return 'Congratulations, You have connected {client_name} to the {service_domain} service!'.format(
            client_name=row['client_name'], service_domain=urllib.parse.urlparse(row['redirect_url']).netloc)
    except db.MissingEntry:
        app.logger.debug('client IP %s does not have any active authentication session', client_ip)
        abort(404)
    except db.TooManyMatches:
    	# (fixme) Intl
        return 'You should have given an url ending with c=N, please use the full url', 404
