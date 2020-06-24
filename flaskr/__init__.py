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
import importlib

from flask import Flask, current_app, request, redirect, url_for, abort

from . import db


app = Flask('g2server', static_folder='g2.server/static', instance_relative_config=True) #pylint: disable=C0103
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'g2server.sqlite'),
)
app.config.from_pyfile('config.py', silent=True)
app.teardown_appcontext(db.close_db)
if 'LOGLEVEL' in app.config:
    app.logger.setLevel(app.config['LOGLEVEL'])


@app.route('/icon.png')
def icon():
    return redirect(url_for('static', filename='icon.png'))


@app.route('/code', methods=['POST'])
def code():
    """Route for the client requesting the authentication on behalf of the user."""

    client_ip = request.access_route[0]
    client_name = request.form['client_name']
    client_hash = request.form['client_hash']
    service_name = request.form['service_name']

    row = db.insert_by_client(client_ip, client_hash, client_name, service_name)

    res = {
        # url that the client present to the user
        'url': current_app.config['G2_SERVER_AUTH_URL'].format(row['g2_server_client_id']),
        # time in secs that the client has to wait before posting a new request
        'interval': 5,
        'expire_in': db.ENTRY_TIMEOUT,
    }
    if row['service_author']:
        res['service_author'] = row['service_author']
        # (fixme) at this point the db entry could be removed!

    app.logger.debug('code(): %s', res)

    return res


@app.route('/auth')
def auth():
    """Route for the user looking to authenticate himself with the 3P service"""

    client_ip = request.access_route[0]

    try:
        g2_server_client_id = request.args.get('c')

        # Call the service specific redirect_url API
        row = db.get_by_user(client_ip, g2_server_client_id)
        service_module = importlib.import_module('.' + row['service_name'], package='flaskr')
        url = service_module.redirect_url()
        app.logger.debug('%s.redirect_url(): %s', row['service_name'], url)
        # (notice) To briefly display a message before the redirection, a refresh based redirect is needed
        return redirect(url)
    except db.MissingEntry:
        app.logger.error('client IP %s does not have any active authentication session', client_ip)
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

        # Call the service specific author API
        row = db.get_by_user(client_ip, g2_server_client_id)
        service_module = importlib.import_module('.' + row['service_name'], package='flaskr')
        service_author = service_module.author(request.args)

        # Update the record with the service_code returned by the 3P service
        db.update_by_user(client_ip, g2_server_client_id, service_author)
        app.logger.debug('%s.author(%s): %s', row['service_name'], request.args, service_author)

        return 'Congratulations, You have connected {client_name} to the {service_name} service!'.format(
            client_name=row['client_name'], service_name=row['service_name'])
    except db.MissingEntry:
        app.logger.error('client IP %s does not have any active authentication session', client_ip)
        abort(404)
    except db.TooManyMatches:
    	# (fixme) Intl
        return 'You should have given an url ending with c=N, please use the full url', 404
