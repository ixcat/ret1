#! /usr/bin/env python

'''
config module -
should be imported before any others
'''

import sys
import logging

import datajoint as dj

dj.config['database.host'] = 'dev01'
dj.config['database.user'] = 'vathes'
dj.config['database.password'] = 'vathes'
dj.config['database.reconnect'] = True

# hack: unspecified key - using for keeping config in same dict
dj.config['myhack.database'] = 'vathes'

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger('demo')

schema = dj.schema(dj.config['myhack.database'], locals())
