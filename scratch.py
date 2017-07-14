
from glob import glob
import scipy.io as sio

projroot = '/home/cat/Workspace/vathes/jobtest/crcns_ret-1'
dataroot = projroot + '/Data'
matfiles = glob(dataroot + '/*.mat')
matdata = []


# 'native' loadmat
# https://docs.scipy.org/doc/scipy/reference/tutorial/io.html

for m in matfiles:
    print('--- ' + m)
    print(str(sio.whosmat(m))) # [('name', (x,y), 'type'), ...]
    matdata.append(sio.loadmat(m))

w0 = sio.whosmat(matfiles[0])
m0 = matfiles[0]
d0 = matdata[0]

# indices be funky
print(str(d0['stimulus'][0,0][5][0]))
print(str(d0['stimulus'][0,0][5][0]['x']))
print(str(d0['stimulus'][0,0][5][0]['y']))



d0.keys()

d0['datainfo']
d0['datainfo'].shape # 1,1

d0['datainfo'][0,0]['date'][0]
d0['datainfo'][0,0]['SmplNo'][0][0]
d0['datainfo'][0,0]['RecNo'][0][0]
d0['datainfo'][0,0]['RecNo'][1][0]

d0['datainfo'][0,0]['RecStartTime'].shape # (2,6)

d0['datainfo'][0,0]['RecStartTime'][0] # array([2008, 7, 3, 1, 28, 30])
list(d0['datainfo'][0,0]['RecStartTime'][0])
tmp = list(d0['datainfo'][0,0]['RecStartTime'][0])
list(d0['datainfo'][0,0]['RecStartTime'][1])

d0['datainfo'][0,0]['Ncell'][0][0]
d0['datainfo'][0,0]['experimenter'][0]
d0['datainfo'][0,0]['description'][0]
d0['datainfo'][0,0]['animal'][0]

d0['stimulus'].shape # 1,2
len(d0['stimulus'][0,0]) # 6?
type(d0['stimulus'][0,0])
d0['stimulus'][0,0][5][0]['x'][0][0][0]

# bookmark : thedata

# using the 'struct_as_record' method:

matdata=[]
for m in matfiles:
    print('--- ' + m)
    print(str(sio.whosmat(m))) # [('name', (x,y), 'type'), ...]
    matdata.append(sio.loadmat(m, struct_as_record=False, squeeze_me=True))

w0 = sio.whosmat(matfiles[0])
m0 = matfiles[0]
d0 = matdata[0]


# dinfo -> recno == nstarttimes; thinking 2x recs per this file

dinfo={}
for k in d0['datainfo']._fieldnames:
    dinfo[k] = d0['datainfo'].__getattribute__(k)



len(d0['stimulus'])
d0['stimulus'][1].type
d0['stimulus'][1].frame
d0['stimulus'][1].onset
d0['stimulus'][1].param._fieldnames
d0['stimulus'][1].param.x
d0['stimulus'][1].param.y
d0['stimulus'][1].param.dx
d0['stimulus'][1].param.dy
d0['stimulus'][1].param.seed

for p in d0['stimulus'][1].param._fieldnames:
    print(str(p) + ' : ' + str(d0['stimulus'][1].param.__getattribute__(p)))

for p in d0['stimulus'][0].param._fieldnames:
    print(str(p) + ' : ' + str(d0['stimulus'][1].param.__getattribute__(p)))

for p in d0['stimulus'][2].param._fieldnames:
    print(str(p) + ' : ' + str(d0['stimulus'][1].param.__getattribute__(p)))
    
for i in range(len(d0['stimulus'])):
    print(str(i) + 'th data')
    for p in d0['stimulus'][i].param._fieldnames:
        print(str(p) + ' : ' + str(d0['stimulus'][1].param.__getattribute__(p)))


len(d0['spikes']) # 12 -> == dinfo['Ncell']
len(d0['spikes'][0]) # 2 -> == nrecs per rec start time
len(d0['spikes'][0][0]) # 5147 -> spikes
len(d0['spikes'][11][0]) # 11629 -> spikes


def grok_meta(data):
    dinfo = {}
    for k in data['datainfo']._fieldnames:
        dinfo[k] = data['datainfo'].__getattribute__(k)

    print('')
    print('experimenter: ' + str(dinfo['experimenter']))
    print('description: ' + str(dinfo['description']))
    print('date: ' + str(dinfo['date']))
    print('sample no: ' + str(dinfo['SmplNo']))
    print('animal: ' + str(dinfo['animal']))
    print('ncell: ' + str(dinfo['Ncell']))
    if type(dinfo['RecNo']) is int:
        print('record: ' + str(dinfo['RecNo']))
        print('start: ' + str(dinfo['RecStartTime']))
        # spikes[cell][spike]
    else:
        print('records:')
        for i in range(len(dinfo['RecNo'])):
            print('record: ' + str(dinfo['RecNo'][i]))
            print('start: ' + str(dinfo['RecStartTime'][i]))
            # spikes[cell][expno][spike]


def grok_file(fname):
    print('--- grok_file: ' + str(fname))
    # [('name', (x,y), 'type'), ...]    
    print('# whosmat' + str(sio.whosmat(fname)))
    data = sio.loadmat(fname, struct_as_record=False, squeeze_me=True)
    
    dinfo = {}
    for k in data['datainfo']._fieldnames:
        dinfo[k] = data['datainfo'].__getattribute__(k)

    print('')
    print('experimenter: ' + str(dinfo['experimenter']))
    print('description: ' + str(dinfo['description']))
    print('date: ' + str(dinfo['date']))
    print('sample no: ' + str(dinfo['SmplNo']))
    print('animal: ' + str(dinfo['animal']))
    print('ncell: ' + str(dinfo['Ncell']))
    if type(dinfo['RecNo']) is int:
        print('record: ' + str(dinfo['RecNo']))
        print('start: ' + str(dinfo['RecStartTime'][0]))
        # spikes[cell][spike]        
    else:
        print('records:')
        for i in range(len(dinfo['RecNo'])):
            print('record: ' + str(dinfo['RecNo'][i]))
            print('start: ' + str(dinfo['RecStartTime'][i]))
            # spikes[cell][expno][spike]            


grok_meta(d0)

for d in matdata:
    grok_meta(d)


for f in matfiles:
    grok_file(f)

# file 20080628_R2 fails 'records' as list
d0 = matdata[5]

'''
bookmark:
- merge update here to 'clean'
- dispatch & print actual lab data info
- rerun/fix any remaining corner cases
DONE
now: dj demoing
'''
import datajoint as dj
dj.config['database.host'] = 'dev01'
dj.config['database.user'] = 'vathes'
dj.config['database.password'] = 'vathes'

schema = dj.schema('vathes', locals())

@schema
class Mouse(dj.Manual):
    definition = """
    mouse_id: int
    ---
    dob: date
    sex: enum('M','F','U')
    """


mouse = Mouse()
mouse.insert1((0, '2017-03-01', 'M'))
mouse.insert1((1, '2017-03-02', 'M'))
mouse.insert1((2, '2017-03-03', 'F'))

mouse.insert([
    (3, '2017-03-04', 'F'),
    (4, '2017-03-05', 'F'),
    (5, '2017-03-06', 'M'),   
])

mouse.fetch() # numpy.ndarray
mouse.fetch(as_dict=True) # OrderedDict
mouse.fetch('dob') # datetime

mouse & 'mouse_id = 0'
(mouse & 'mouse_id = 0').delete()

@schema
class Session(dj.Manual):
    definition = """
    # experiment session
    -> Mouse
    session_date: date
    ---
    experiment_setup: int
    experimenter: varchar(128)
    """

session = Session()
session.insert1((1, '2017-06-01', 0, 'joe schmo'))

(mouse & 'mouse_id = 1').delete()



# dictfoo mio5
# st0
# obj._fieldnames = ['a','b','c']


# more packfoo
cell=0
expid=0

type(cf.spikes)
len(cf.spikes)
cf.spikes.dtype

type(cf.spikes[cell])
len(cf.spikes[cell])
cf.spikes[cell].dtype

type(cf.spikes[cell][expid])
len(cf.spikes[cell][expid])
cf.spikes[cell][expid].dtype

cf_swap = np.swapaxes(cf.spikes, 0, 1)

type(cf_swap[expid])
len(cf_swap[expid])
cf_swap[expid].dtype

type(cf_swap[expid])
len(cf_swap[expid])
cf_swap[expid].dtype

type(cf_swap[expid][cell])
len(cf_swap[expid][cell])
cf_swap[expid][cell].dtype

oneset = cf_swap[0]

# not many - nested? oneset.tobytes()
# very meany oneset[0].tobytes()

oneset_flat = oneset.flatten()


# ...

mf = '/home/cat/Workspace/vathes/jobtest/crcns_ret-1/Data/20080628_R2.mat'
cf = process_file(mf)
cf = util.CrcnsFile(mf)
cf.load()
experiment_data.insert_crcns(cf)

