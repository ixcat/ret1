#! /usr/bin/env python

'''
config module -
should be imported before any others
'''

import os
import sys
import logging

import datajoint as dj

defaults = {
    'database.host': 'localhost',
    'database.user': 'vathes',
    'database.password': 'vathes',
    'database.reconnect': True,  # note: overriding dj defaults here
    'database.schema': 'vathes',  # hack: unspecified dj.config key
}

dj.config['database.host'] = os.getenv('DJ_HOST')
dj.config['database.user'] = os.getenv('DJ_USER')
dj.config['database.password'] = os.getenv('DJ_PASS')
dj.config['database.reconnect'] = os.getenv('DJ_RECONNECT')
dj.config['database.schema'] = os.getenv('DJ_SCHEMA')

for dk in defaults.keys():
    if dj.config[dk] is None:
        dj.config[dk] = defaults[dk]

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger('demo')

schema = dj.schema(dj.config['database.schema'], locals())
