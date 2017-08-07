#! /usr/bin/env python

import pymysql as db
import numpy as np
import datajoint as dj

from pymysql import IntegrityError

from .config import log

schema = dj.schema(dj.config['database.schema'], locals())


def schema_hacks():
    # todo: actual updated pretty-print sql
    experiment_data_pp = '''show tables;'''
    c = db.connect(
        user=dj.config['database.user'],
        host=dj.config['database.host'],
        password=dj.config['database.password'],
        database=dj.config['database.schema']
    )
    c.query(experiment_data_pp)
    c.commit()


@schema
class Animal(dj.Manual):
    definition = '''
    animal_id: integer auto_increment
    ---
    # Note: dj unique use not? documented. +1 relying on undefined behavior.
    # could alternately be code level check or switch to text pkey,
    # or maybe this is a goo1d thing to codify..
    animal_desc: varchar(128) unique
    '''

    def fetch_crcns(self, crcns):
        q = str('animal_desc = "' + crcns.animal + '"')
        log.debug('Animal::fetch_crcns(): q: ' + q)
        return (self & q).fetch(as_dict=True)

    def insert_crcns(self, crcns):
        log.debug('Animal::insert_crcns(): crcns.animal: ' + str(crcns.animal))
        self.insert1((None, crcns.animal))


@schema
class Session(dj.Manual):
    definition = '''
    -> Animal
    date: integer
    sample_no: integer
    ---
    experimenter: varchar(128)
    # ncells / nrecords, or records? or needed? (can be computed via db)
    ncells: integer
    nrecords: integer
    '''

    def fetch_crcns(self, crcns):

        animal = Animal()
        subj = animal.fetch_crcns(crcns)
        aq = str('animal_id = ' + str(subj[0]['animal_id']))
        dq = str('date = ' + str(crcns.date))
        sq = str('sample_no = ' + str(crcns.sampleno))

        log.debug('ExperimentMeta::fetch_crcns(): '
                  + 'aq: ' + aq
                  + 'dq: ' + dq
                  + 'sq: ' + sq)

        return (self & aq & dq & sq).fetch(as_dict=True)

    def insert_crcns(self, crcns):

        animal = Animal()
        subj = animal.fetch_crcns(crcns)

        if len(subj) > 1:
            raise IntegrityError('error: more than 1 animal:' + crcns.animal)

        if len(subj) == 0:
            # hmm: do insert here or raise error?
            animal.insert_crcns(crcns)
            subj = animal.fetch_crcns(crcns)

        subj_id = subj[0]['animal_id']

        insert_tup = (
            subj_id,
            crcns.date,
            crcns.sampleno,
            crcns.experimenter,
            crcns.ncell,
            len(crcns.recno),
        )

        log.debug('Session::insert_crcns(): insert_tup: '
                  + str(insert_tup))

        self.insert1(insert_tup)


@schema
class Experiment(dj.Manual):
    definition = '''
    -> Session
    record: integer
    ---
    start: timestamp
    st_nframes: integer
    st_frame: double
    st_onset: double
    st_pixelsize: float
    st_type: varchar(128)
    st_param_x: integer
    st_param_y: integer
    st_param_dx: integer
    st_param_dy: integer
    st_param_seed: integer
    '''

    def fetch_crcns(self, crcns, recno=None):
        '''
        Table where file is not 1:1 with query since 1:M in record
        either:
        1) have separate methods
        2) single with optional recno defaulting to all
        3) single with optional recno defaulting to 1st
        going with #2, since it corresponds with relation to file
        '''
        session = Session()
        cur_session = session.fetch_crcns(crcns)

        if len(cur_session) > 1:
            raise IntegrityError('error: duplicate sessions')

        cur_session = cur_session[0]

        aq = str('animal_id = ' + str(cur_session['animal_id']))
        dq = str('date = ' + str(crcns.date))
        sq = str('sample_no = ' + str(crcns.sampleno))

        result = None
        if recno is None:
            log.debug('ExperimentMeta::fetch_crcns(recno=None): '
                      + 'aq: ' + aq
                      + 'dq: ' + dq
                      + 'sq: ' + sq)

            result = (self & aq & dq & sq).fetch(as_dict=True)
        else:
            rq = str('record = ' + str(recno))

            log.debug('ExperimentMeta::fetch_crcns(recno=' + str(recno) + '): '
                      + 'aq: ' + aq
                      + 'dq: ' + dq
                      + 'sq: ' + sq
                      + 'rq: ' + rq)

            result = (self & aq & dq & sq & rq).fetch(as_dict=True)

        return result

    def insert_crcns(self, crcns):
        for i in range(len(crcns.recno)):
            self.insert_crcns_recno(crcns, i)

    def insert_crcns_recno(self, crcns, idx):
        session = Session()
        cur_session = session.fetch_crcns(crcns)

        if len(cur_session) > 1:
            raise IntegrityError('error: duplicate sessions')

        cur_session = cur_session[0]
        l = []
        l.append(cur_session['animal_id'])
        l.append(cur_session['date'])
        l.append(cur_session['sample_no'])
        l.append(crcns.recno[idx])

        l.append(crcns.recstart[idx])
        l.append(crcns.stimulus[idx]['Nframes'])
        l.append(crcns.stimulus[idx]['frame'])
        l.append(crcns.stimulus[idx]['onset'])
        l.append(crcns.stimulus[idx]['pixelsize'])
        l.append(crcns.stimulus[idx]['type'])
        l.append(crcns.stimulus[idx]['param']['x'])
        l.append(crcns.stimulus[idx]['param']['y'])
        l.append(crcns.stimulus[idx]['param']['dx'])
        l.append(crcns.stimulus[idx]['param']['dy'])
        l.append(crcns.stimulus[idx]['param']['seed'])

        self.insert1(l)


@schema
class Spikes(dj.Manual):
    definition = '''
    -> Experiment
    cell: integer
    ---
    spikes: longblob
    '''

    def fetch_crcns(self, crcns, recno=None, cellno=None):
        raise NotImplementedError

    def insert_crcns(self, crcns):
        for i in range(len(crcns.recno)):
            for j in range(len(crcns.spikes)):
                self.insert_crcns_spikes(crcns, i, j)

    def insert_crcns_spikes(self, crcns, recidx, cellno):

        recno = crcns.recno[recidx]
        experiment = Experiment()
        cur_experiment = experiment.fetch_crcns(crcns, recno)

        if len(cur_experiment) > 1:
            raise IntegrityError('error: duplicate experiments')

        cur_experiment = cur_experiment[0]

        l = []
        l.append(cur_experiment['animal_id'])
        l.append(cur_experiment['date'])
        l.append(cur_experiment['sample_no'])
        l.append(recno)
        l.append(cellno)

        l.append(crcns.spikes[cellno][recidx])

        log.info('Spikes::insert_crcns(): insert_tup: '
                 + str(l))

        self.insert1(l)
