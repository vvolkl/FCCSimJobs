#python printdict.py /afs/cern.ch/user/h/helsens/www/FCCsim_v01.txt
import json
import sys
import os.path
import re

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
indictname='eventsDict.json'
with open(indictname) as f:
    indict = json.load(f)


for s, value in sorted(indict.items()):
    evttot=0
    njobs=0
    nbad=0
    print '------------------------------- ',s
    outdir="/eos/experiment/fcc/hh/simulation/samples/"+s
    nfileseos=len(os.listdir(outdir))
    for j in value:
        if j['status']=='DONE':
            evttot+=int(j['nevents'])
            njobs+=1
        elif j['status']=='BAD':
            nbad+=1
        else:
            print 'UNKNOWN STATUS ',j['status']
    cmd='%s,,%s,,%i,,%i,,%i\n'%(outdir,comma_me(str(evttot)),njobs,nfileseos,nbad)
    OutFile.write(cmd)               
    ntot_events+=int(evttot)
    ntot_files+=int(njobs)
    ntot_files_bad+=int(nbad)

cmd='%s,,%s,,%s,,%i,,%i\n'%('total',comma_me(str(ntot_events)),'',ntot_files,ntot_files_bad)
OutFile.write(cmd)
