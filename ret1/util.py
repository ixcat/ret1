#! /usr/bin/env python

import scipy.io as sio
from scipy.io.matlab.mio5_params import mat_struct as mat_struct


def mat_struct_to_dict(ms):
    dct = {}
    for k in ms._fieldnames:
        v = ms.__getattribute__(k)
        if type(v) is mat_struct:
            dct[k] = mat_struct_to_dict(v)  # may the stack be with us...
        else:
            dct[k] = v

    return dct


class CrcnsFile(object):

    def __init__(self, fname=None):
        self._data = None
        self.fname = fname
        self.experimenter = None
        self.description = None
        self.date = None
        self.sampleno = None
        self.animal = None
        self.ncell = None
        self.recno = None
        self.recstart = None
        self.stimulus = None
        self.spikes = None

    def load(self, fname=None):
        if fname is None and self.fname is None:
            raise Exception('CrcnsFile::load(): no file given')
        if fname is not None:
            self.fname = fname

        self._data = sio.loadmat(self.fname, struct_as_record=False,
                                 squeeze_me=True)

        dinfo = {}
        for k in self._data['datainfo']._fieldnames:
            dinfo[k] = self._data['datainfo'].__getattribute__(k)

        self.experimenter = dinfo['experimenter']
        self.description = dinfo['description']
        self.date = dinfo['date']
        self.sampleno = dinfo['SmplNo']
        self.animal = dinfo['animal']
        self.ncell = dinfo['Ncell']
        self.recno = dinfo['RecNo']
        self.recstart = dinfo['RecStartTime']
        self.stimulus = self._data['stimulus']
        self.spikes = self._data['spikes']
        self._normalize()

    def dateconv(lst):
        return '%4.4i-%2.2i-%2.2i %2.2i:%2.2i:%2.2i' % tuple(lst)

    def _normalize(self):
        '''
        Attempt to normalize loaded _data for uniformity -
        lesser of evils between loadmat's squeeze_me excessively flattening
        or alternately dealing with many layers of 0-length arrays
        FIXME?: single record w/ single cell case will fail -
        ... spikes shape in ncell==1 different than recno fixups expect
        ... doesn't apply to current test data, so defer.
        '''
        # shape fixing for 1x record
        if type(self.recno) is int:
            self.recno = [self.recno]
            # hmm - is always array or AoA; hack here rather than deciphering
            self.recstart = [self.recstart]
            # spikes[cell][spike] -> spikes[cell][expno==0][spike]
            self.spikes.resize([len(self.spikes), 1])
            '''
            # XXX: to be deleted
            for c in range(len(self.spikes)):
                print('CrcnsFile._normalize(): spikenormal')
                print('before')
                print(len(self.spikes))
                print(str(self.spikes.shape))
                print(len(self.spikes[c]))
                print(str(self.spikes[c].shape))
                # hmm.. should be getting:
                # ValueError: cannot resize this array: ...
                self.spikes[c].resize([1, len(self.spikes[c])])
                print('after')
                print(len(self.spikes))
                print(str(self.spikes.shape))
                print(len(self.spikes[c]))
                print(str(self.spikes[c].shape))
            '''

        # shape fixing for 1x cell
        if self.ncell == 1:
            self.spikes = [self.spikes]  # XXX: ndarray?

        # de-matlabify stimulus data
        new_stimulus = []  # XXX: ndarray?

        if type(self.stimulus) is mat_struct:
            self.stimulus = [self.stimulus]

        for i in range(len(self.stimulus)):
            s = self.stimulus[i]
            dct = mat_struct_to_dict(s)
            new_stimulus.append(dct)

        self.stimulus = new_stimulus

        # stringify date array
        l = []
        for i in range(len(self.recstart)):
            l.append(CrcnsFile.dateconv(self.recstart[i]))
        self.recstart = l

    def print_meta(self):
        '''
        dump file metadata, also perform some simple assertions
        misc: filename seems to be {DATE}_R{SAMPLENO}.mat
        '''
        print('---')
        print('fname: ' + str(self.fname))
        # [('name', (x,y), 'type'), ...]
        print('whosmat: "' + str(sio.whosmat(self.fname)) + '"')

        print('experimenter: ' + str(self.experimenter))
        print('description: ' + str(self.description))
        print('date: ' + str(self.date))
        print('sample no: ' + str(self.sampleno))
        print('animal: ' + str(self.animal))
        print('ncell: ' + str(self.ncell))

        # spikes[cell][expno][spike]
        try:
            assert(len(self.spikes) == self.ncell)
        except AssertionError:
            print("error - data['spikes'] " + str(len(self.spikes))
                  + ' : ' + str(self.ncell))
            raise

        print('stimulus: ')
        assert(len(self.stimulus) == len(self.recno))
        for s in self.stimulus:
            print('  - ')
            for k in s:
                print('    ' + str(k) + ' : ' + str(s[k]))

        print('records: # nrecs: ' + str(len(self.recno)))
        for i in range(len(self.recno)):
            print('  -')
            print('    record: ' + str(self.recno[i]))
            print('    start: ' + str(self.recstart[i]))
            print('    spikes: ')
            for j in range(len(self.spikes)):
                print('      - ' + str(len(self.spikes[j][i])))
