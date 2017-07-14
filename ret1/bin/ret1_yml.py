#! /usr/bin/env python

'''
crcns_yml.py: dump CrcnsFile metadata to stdout in ymlish format
'''

import sys
import os.path

from glob import glob

from ret1.util import CrcnsFile

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: ' + os.path.basename(sys.argv[0]) + ' datadir')
        sys.exit(0)

    dataroot = sys.argv[1]
    matfiles = glob(dataroot + '/*.mat')

    print("files: " + str(matfiles))
    for mf in matfiles:
        cf = CrcnsFile(mf)
        cf.load()
        cf.print_meta()
