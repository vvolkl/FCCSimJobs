#python printdict.py /afs/cern.ch/user/h/helsens/www/FCCsim_v01.txt
import json
import sys
import os.path
import re
import users as us

if len(sys.argv)!=2:
    print 'usage: python printdict.py outfile.txt'
    exit(3)


def comma_me(amount):
    orig = amount
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', amount)
    if orig == new:
        return new
    else:
        return comma_me(new)

OutFile   = open(sys.argv[1], 'w')
ntot_events=0
ntot_files=0
ntot_files_bad=0
indict=None
indictname='/afs/cern.ch/work/h/helsens/public/FCCDicts/SimulationDict_v01.json'
with open(indictname) as f:
    indict = json.load(f)

for s, value in sorted(indict.items()):
    evttot=0
    njobs=0
    nbad=0
    print '------------------------------- ',s
    outdir="/eos/experiment/fcc/hh/simulation/samples/"+s
    nfileseos=len(os.listdir(outdir))
    mapusers=[]
    for j in value:
        if j['status']=='DONE':
            evttot+=int(j['nevents'])
            njobs+=1
        elif j['status']=='BAD':
            nbad+=1
        else:
            print 'UNKNOWN STATUS ',j['status']

        for key, value in us.users.iteritems():
            if key in j['out']:
                mapusers.append(key)

    toaddus=''
    for key, value in us.users.iteritems():
        njobuser=sum(1 for ii in mapusers if ii == key)
        print 'user %s has njobs %i meaning %i'%(key,njobuser,int(100*njobuser/nfileseos))
        toaddus+=',,%i'%(100*njobuser/nfileseos)
    
    print 'toaddus  ',toaddus
    cmd='%s,,%s,,%i,,%i,,%i%s\n'%(outdir,comma_me(str(evttot)),njobs,nfileseos,nbad,toaddus)
    OutFile.write(cmd)               
    ntot_events+=int(evttot)
    ntot_files+=int(njobs)
    ntot_files_bad+=int(nbad)

cmd='%s,,%s,,%s,,%i,,%i\n'%('total',comma_me(str(ntot_events)),'',ntot_files,ntot_files_bad)
OutFile.write(cmd)
