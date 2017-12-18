import glob, os, sys,subprocess,cPickle
import commands
import time
import random
from datetime import datetime

#__________________________________________________________
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}

#__________________________________________________________
def SubmitToBatch(cmd,nbtrials):
    submissionStatus=0
    for i in range(nbtrials):            
        outputCMD = getCommandOutput(cmd)
        stderr=outputCMD["stderr"].split('\n')

        for line in stderr :
            if line=="":
                print "------------GOOD SUB"
                submissionStatus=1
                break
            else:
                print "++++++++++++ERROR submitting, will retry"
                print "error: ",stderr
                print "Trial : "+str(i)+" / "+str(nbtrials)
                time.sleep(10)
                break
            
        if submissionStatus==1:
            jobid=outputCMD["stdout"].split()[1].replace("<","").replace(">","")
            return 1,jobid
        
        if i==nbtrials-1:
            print "failed sumbmitting after: "+str(nbtrials)+" trials, will exit"
            return 0,0

#__________________________________________________________
if __name__=="__main__":
    Dir = os.getcwd()
    
    user=os.environ['USER']

    import argparse
    simparser = argparse.ArgumentParser()
    geoTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Which calorimeters to include (always include beampipe and tracker)
    geoTypeGroup.add_argument("--geoFull", action='store_true', help="Full geometry assembly (barrel, endcaps, forward) (default)")
    geoTypeGroup.add_argument("--geoBarrel", action='store_true', help="Only calo barrel")
    simparser.add_argument("--bFieldOff", action='store_true', help="Switch OFF magnetic field (default: B field ON)")

    simparser.add_argument('-s','--seed', type=int, help='Seed for the random number generator', required=True)
    simparser.add_argument('-n','--numEvents', type=int, help='Number of simulation events per job', required=True)
    simparser.add_argument('-N','--numJobs', type=int, default = 10, help='Number of jobs to submit')
    simparser.add_argument('--jobOptions', type=str, default = 'config/geantSim.py', help='Name of the job options run by FCCSW (default config/geantSim.py')
    simparser.add_argument('-o','--output', type=str, help='NamePath of the output on EOS', required=True)

    genTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Type of events to generate
    genTypeGroup.add_argument("--singlePart", action='store_true', help="Single particle events")
    genTypeGroup.add_argument("--minBias", action='store_true', help="Minimum bias events generated with Pythia")
    genTypeGroup.add_argument("--LHE", action='store_true', help="LHE events + Pythia")

    from math import pi
    singlePartGroup = simparser.add_argument_group('Single particles')
    singlePartGroup.add_argument('-e','--energy', type=int, required = True, help='Energy of particle in GeV')
    singlePartGroup.add_argument('--etaMin', type=float, default=0., help='Minimal pseudorapidity')
    singlePartGroup.add_argument('--etaMax', type=float, default=0., help='Maximal pseudorapidity')
    singlePartGroup.add_argument('--phiMin', type=float, default=0, help='Minimal azimuthal angle')
    singlePartGroup.add_argument('--phiMax', type=float, default=2*pi, help='Maximal azimuthal angle')
    singlePartGroup.add_argument('--particle', type=int,  required = True, help='Particle type (PDG)')

    pythiaGroup = simparser.add_argument_group('Pythia','Common for min bias and LHE')
    pythiaGroup.add_argument('-c', '--card', type=str, default='PythiaCards/default.cmd', help='Path to Pythia card (default: PythiaCards/default.cmd)')

    lheGroup = simparser.add_argument_group('LHE','Additional for generation with LHE')
    lheGroup.add_argument('--process', type=str, help='Event type [Zee, Haa, Hbb, Wqq, Zqq, t, ljet]')
    lheGroup.add_argument('--pt', type=int, help='Transverse momentum of simulated jets')
    simargs, _ = simparser.parse_known_args()

    batchGroup = simparser.add_mutually_exclusive_group(required = True) # Wher to submit jobs
    batchGroup.add_argument("--lsf", action='store_true', help="Submit with LSF")
    batchGroup.add_argument("--condor", action='store_true', help="Submit with condor")

    lsfGroup = simparser.add_argument_group('Pythia','Common for min bias and LHE')
    lsfGroup.add_argument('-q', '--queue', type=str, default='8nh', help='lxbatch queue (default: 8nh)')

    simargs, _ = simparser.parse_known_args()

    print "=================================="
    print "==      GENERAL SETTINGS       ==="
    print "=================================="
    magnetic_field = not simargs.bFieldOff
    num_events = simargs.numEvents
    num_jobs = simargs.numJobs
    job_options = simargs.jobOptions
    seed = simargs.seed
    output_path = simargs.output
    print "B field: ", magnetic_field
    if simargs.geoFull:
        print "full geometry assembly"
    elif simargs.geoBarrel:
        print "only barrel"
    print "number of events = ", num_events
    print "seed: ", seed
    print "output path: ", output_path
    if simargs.singlePart:
        energy = simargs.energy
        etaMin = simargs.etaMin
        etaMax = simargs.etaMax
        phiMin = simargs.phiMin
        phiMax = simargs.phiMax
        pdg = simargs.particle
        particle_human_names = {11: 'electron', -11: 'positron', -13: 'mup', 13: 'mum', 22: 'photon', 111: 'pi0', 211: 'pip', -211: 'pim'}
        particle_geant_names = {11: 'e-', -11: 'e+', -13: 'mu+', 13: 'mu-', 22: 'gamma', 111: 'pi0', 211: 'pi+', -211: 'pi-' }
        print "=================================="
        print "==       SINGLE PARTICLES      ==="
        print "=================================="
        print "particle PDG, name: ", pdg, " ", particle_human_names[pdg], " ", particle_geant_names[pdg]
        print "energy: ", energy, "GeV"
        if etaMin == etaMax:
            print "eta: ", etaMin
        else:
            print "eta: from ", etaMin, " to ", etaMax
        if phiMin == phiMax:
            print "phi: ", phiMin
        else:
            print "phi: from ", phiMin, " to ", phiMax
    elif simargs.minBias:
        card = simargs.card
        print "=================================="
        print "==           MIN BIAS          ==="
        print "=================================="
        print "card = ", card
    elif simargs.LHE:
        card = simargs.card
        lhe_type = simargs.process
        pt = simargs.pt
        print "=================================="
        print "==             LHE             ==="
        print "=================================="
        print "card: ", card
        print "LHE type: ", lhe_type
        print "jet pt: ", pt
        print "=================================="
    if simargs.condor:
        print "submitting to condor ..."
    elif simargs.lsf:
        print "submitting to lxbatch ..."
        queue = simargs.queue
        print "queue: ", queue

    produceLHE = simargs.LHE
    rundir = os.getcwd()
    nbjobsSub=0

    for i in xrange(num_jobs):
        seed = int(datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
        uniqueID='%s_%i'%(user,seed)
        
        # logdir=Dir+"/BatchOutputs/"
        # os.system("mkdir -p %s"%logdir)
        # cardname=card.split('/')[-1]
        # frunname = 'job_%s_%s.sh'%(cardname.replace('.cmd',''),uniqueID)
        # outfile = 'output_%s.root'%(uniqueID)
        # outfileconv = outfile.replace('.root','_converted.root')

        # frun = None
        # try:
        #     frun = open(logdir+'/'+frunname, 'w')
        # except IOError as e:
        #     print "I/O error({0}): {1}".format(e.errno, e.strerror)
        #     time.sleep(10)
        #     frun = open(logdir+'/'+frunname, 'w')


        # commands.getstatusoutput('chmod 777 %s/%s'%(logdir,frunname))
        # frun.write('#!/bin/bash\n')
        # frun.write('unset LD_LIBRARY_PATH\n')
        # frun.write('unset PYTHONHOME\n')
        # frun.write('unset PYTHONPATH\n')
        # frun.write('export JOBDIR=$PWD\n')
        # frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/\n')
        # frun.write('source ./init.sh\n')
        # frun.write('export EOS_MGM_URL=\"root://eospublic.cern.ch\"\n')

        # if produceLHE:
        #     frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Generators/FlatGunLHEventProducer\n')

        #     if process=='ljets':
        #         frun.write('python flatGunLHEventProducer.py   --pdg 1 2 3   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(num_events,pt,pt,seed))
        #     elif process=='bjets':
        #         frun.write('python flatGunLHEventProducer.py   --pdg 5   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(num_events,pt,pt,seed))
        #     elif process=='top':
        #         frun.write('python flatGunLHEventProducer.py   --pdg 6   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(num_events,pt,pt,seed))
        #     elif process=='Z':
        #         frun.write('python flatGunLHEventProducer.py   --pdg 23   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(num_events,pt,pt,seed))
        #     elif process=='W':
        #         frun.write('python flatGunLHEventProducer.py   --pdg 24   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(num_events,pt,pt,seed))
        #     elif process=='H':
        #         frun.write('python flatGunLHEventProducer.py   --pdg 25   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(num_events,pt,pt,seed))
        #     else:
        #         print 'process does not exists, exit'
        #         sys.exit(3)
        #     frun.write('gunzip $JOBDIR/events.lhe.gz\n')
        #     frun.write('cp %s $JOBDIR/card.cmd\n'%(card))
        #     frun.write('echo "Beams:LHEF = $JOBDIR/events.lhe" >> $JOBDIR/card.cmd\n')
        #     frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/\n')
        #     frun.write('./run fccrun.py  %s  --outputfile=$JOBDIR/%s --nevents=%i --inputfile=$JOBDIR/card.cmd\n'%(job_options, outfile ,num_events))

        # else:
        #     frun.write('./run fccrun.py  %s  --outputfile=$JOBDIR/%s --nevents=%i --inputfile=%s\n'%(job_options, outfile ,num_events, card))

        # frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/\n')
        # frun.write('python eoscopy.py $JOBDIR/%s %s\n'%(outfile,output_path))

        # cmdBatch="bsub -M 4000000 -R \"pool=40000\" -q %s -cwd%s %s" %(queue, logdir,logdir+'/'+frunname)
        # batchid=-1
        # job,batchid=SubmitToBatch(cmdBatch,10)
        # nbjobsSub+=job

    print 'succesfully sent %i  jobs'%nbjobsSub
