#! /usr/bin/env python

import sys
import os.path
from importlib import reload
from glob import glob

from pymysql.err import IntegrityError

from ret1.config import log
import ret1.util as util
import ret1.schema as schema

if len(sys.argv) < 2:
    print('usage: ' + os.path.basename(sys.argv[0]) + ' datadir')
    sys.exit(0)


ONEFILE = False

schema.schema.drop(force=True)
reload(schema)
schema.schema_hacks()

animal = schema.Animal()
session = schema.Session()
experiment = schema.Experiment()
spikes = schema.Spikes()


dataroot = sys.argv[1]
# dataroot = '/usr/home/cat/Workspace/vathes/example/crcns_ret-1/Data'
# TODO: need to also load in the random data - so should be top level dir
matfiles = glob(dataroot + '/*.mat')


def process_file(fname):
    cf = util.CrcnsFile(fname)
    cf.load()
    cf.print_meta()
    log.info('animal.insert_crcns')

    try:
        animal.insert_crcns(cf)
    except IntegrityError:
        log.info('animal.insert_crcns: duplicate animal')

    log.info('session.insert_crcns')
    session.insert_crcns(cf)

    log.info('experiment.insert_crcns')
    experiment.insert_crcns(cf)

    log.info('spikes.insert_crcns')
    spikes.insert_crcns(cf)


if ONEFILE is True:
    process_file(matfiles[0])
else:
    for mf in matfiles:
        log.info('# processing file: ' + mf)
        process_file(mf)
