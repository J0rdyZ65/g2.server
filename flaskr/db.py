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

import time
import sqlite3
from itertools import count, filterfalse

from flask import current_app, g

class DBException(Exception):
    pass

class MissingEntry(DBException):
    pass

class TooManyMatches(DBException):
    pass

ENTRY_TIMEOUT = (5*60) # 5mins


def get_db():
    if 'dbc' not in g:
        g.dbc = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.dbc.row_factory = sqlite3.Row
    return g.dbc


def close_db(_e=None):
    dbc = g.pop('dbc', None)

    if dbc is not None:
        dbc.close()


def insert_by_client(client_ip, client_hash, client_name, service_name):
    dbc = get_db()
    client_ip_entries = sql_select(dbc, 'SELECT * FROM OAuth2 WHERE client_ip = ?', client_ip)
    client_hash_entries = [e for e in client_ip_entries if e['client_hash'] == client_hash]
    if client_hash_entries:
        g2_server_client_id = client_hash_entries[0]['g2_server_client_id']
        service_author = client_hash_entries[0]['service_author']
        expire = client_hash_entries[0]['expire']
    else:
        g2_server_client_id = next(filterfalse(set([r['g2_server_client_id'] for r in client_ip_entries]).__contains__, count(1)))
        service_author = ''
        expire = time.time() + ENTRY_TIMEOUT
    with dbc as dbt:
        dbt.execute('REPLACE INTO '
                    'OAuth2 (client_ip, client_hash, client_name, g2_server_client_id, service_name, service_author, expire) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (client_ip, client_hash, client_name, g2_server_client_id, service_name, service_author, expire))
    return {
        # Return the server generated info
        'g2_server_client_id': g2_server_client_id,
        'service_author': service_author,
    }


def get_by_user(client_ip, g2_server_client_id):
    dbc = get_db()
    if g2_server_client_id:
        client_entries = sql_select(dbc, 'SELECT * FROM OAuth2 WHERE client_ip = ? and g2_server_client_id = ?',
                                    client_ip, g2_server_client_id)
        if not client_entries:
            raise MissingEntry
    else:
        client_entries = sql_select(dbc, 'SELECT * FROM OAuth2 WHERE client_ip = ?', client_ip)
        if not client_entries:
            raise MissingEntry
        if len(client_entries) > 1:
            raise TooManyMatches
    return client_entries[0]


def update_by_user(client_ip, g2_server_client_id, service_author):
    dbc = get_db()
    with dbc as dbt:
        if g2_server_client_id:
            dbt.execute('UPDATE OAuth2 SET service_author = ? WHERE client_ip = ? and g2_server_client_id = ?',
                        (service_author, client_ip, g2_server_client_id))
        else:
            dbt.execute('UPDATE OAUth2 SET service_author = ? WHERE client_ip = ?',
                        (service_author, client_ip))


def sql_select(dbc, sql, *args):
    return [r for r in dbc.execute(sql, args) if r['expire'] > time.time()]
