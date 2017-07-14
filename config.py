#! /usr/bin/env python

'''
config module - 
should be imported before any others via 'from config import *'
'''

import sys
import os, os.path
import logging
from glob import glob
from importlib import reload

import pymysql as db
import datajoint as dj
import numpy as np

from pymysql.err import IntegrityError

dj.config['database.host'] = 'dev01'
dj.config['database.user'] = 'vathes'
dj.config['database.password'] = 'vathes'
dj.config['database.reconnect'] = True

# hack: unspecified key - using for keeping config in same dict
dj.config['myhack.database'] = 'vathes'

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger('demo')

schema = dj.schema(dj.config['myhack.database'], locals())
