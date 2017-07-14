#! /usr/bin/env python

from config import *

schema = dj.schema(dj.config['myhack.database'], locals())

def schema_hacks():
    experiment_data_pp = '''
    create view _experiment_data_pp as
    select 
    animal_id, date, sample_no, record, cell, 
    start, st_nframes, st_frame, st_onset, st_pixelsize, st_type,
    st_param_x, st_param_y, st_param_dx, st_param_dy, st_param_seed,
    length(spikes)
    from _experiment_data;
    '''
    c = db.connect(
        user=dj.config['database.user'],
        host=dj.config['database.host'],
        password=dj.config['database.password'],
        database=dj.config['myhack.database']
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
    # or maybe this is a good thing to codify..
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
class ExperimentMeta(dj.Manual):
    '''
    TODO: Stimulus data???
    '''
    definition = '''
    -> Animal
    date: integer
    sample_no: integer
    ---
    experimenter: varchar(128)
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
            raise IntegrityError('error: more than 1 animal for:' + cf.animal)

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
            len(crcns.recno),)

        log.debug('ExperimentMeta::insert_crcns(): insert_tup: '
                  + str(insert_tup))

        self.insert1(insert_tup)


@schema
class ExperimentData(dj.Imported):
    '''
    XXX: fixme sloppy table normalization - 
    better would be params:experiment 1:1,
    and cell:experiment 1:1,
    for now, geting imports working...
    '''
    definition = '''
    -> ExperimentMeta
    record: integer
    cell: integer
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
    spikes: longblob
    '''
    def insert_crcns(self, crcns):
        for i in range(len(crcns.recno)):
            self.insert_crcns_recno(crcns, i)

    def insert_crcns_recno(self, crcns, idx):
        experiment_meta = ExperimentMeta()
        meta = experiment_meta.fetch_crcns(crcns)

        if len(meta) > 1:
            raise IntegrityError('error: duplicate experiment metadata')

        l = []
        l.append(meta[0]['animal_id'])
        l.append(meta[0]['date'])
        l.append(meta[0]['sample_no'])
        l.append(crcns.recno[idx])
        l.append(None) # cell placeholder

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

        # spikes[cell][expno][spike] -> spikes[expno][cell][spike]
        # grr:
        # .spikes.dtype -> dtype('O')
        # .spikes[0].dtype -> dtype('O')
        # .spikes[0][0].dtype -> dtype('<f8')
        # ... here: >>> np.dtype('<f8') -> dtype('float64')
        # dtype('O') not serialized in dj; so 1 record per cell

        # ../crcns_ret-1/Data/20080628_R2.mat
        # only has 1 record; so swapaxes doesn't "do"

        spike_swap = np.swapaxes(crcns.spikes, 0, 1)
        for i in range(len(spike_swap[idx])):
            l2 = l.copy()
            l2[4] = i
            l2.append(spike_swap[idx][i])

            log.debug('ExperimentMeta::insert_crcns(): insert_tup: '
                      + str(l2))

            self.insert1(l2)


