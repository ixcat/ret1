#! /usr/bin/env python

from config import *

import util
import schema

def oldmain():
    animal = schema.Animal()
    try:
        animal.insert1((None, 'yoyo',))
    except IntegrityError:
        log.info('test note: duplicate animal insert attempted')
    experiment_meta = schema.ExperimentMeta()
    experiment_data = schema.ExperimentData()

if len(sys.argv) < 2:
    print('usage: ' + os.path.basename(sys.argv[0]) + ' datadir')
    sys.exit(0)

schema.schema.drop(force=True)
reload(schema)
schema.schema_hacks()

animal = schema.Animal()
experiment_meta = schema.ExperimentMeta()
experiment_data = schema.ExperimentData()
    
dataroot = sys.argv[1]
# dataroot = '/home/cat/Workspace/vathes/jobtest/crcns_ret-1/Data'
matfiles = glob(dataroot + '/*.mat')

def process_file(fname):
    cf = util.CrcnsFile(mf)
    cf.load()
    cf.print_meta()
    log.info('animal.insert_crcns')

    try:
        animal.insert_crcns(cf)
    except IntegrityError:
        log.info('animal.insert_crcns: duplicate animal')

    log.info('experiment_meta.insert_crcns')
    experiment_meta.insert_crcns(cf)

    log.info('experiment_data.insert_crcns')
    experiment_data.insert_crcns(cf)
    return cf
    

for mf in matfiles:
    log.info('# processing file: ' + mf)
    process_file(mf)

