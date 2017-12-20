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

# ToDo: unify both submit: 
#__________________________________________________________
def SubmitToLsf(cmd,nbtrials):
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
def SubmitToCondor(cmd,nbtrials):
    submissionStatus=0
    for i in xrange(nbtrials):            
        outputCMD = getCommandOutput(cmd)
        stderr=outputCMD["stderr"].split('\n')
        stdout=outputCMD["stdout"].split('\n')

        if len(stderr)==1 and stderr[0]=='' :
            print "------------GOOD SUB"
            submissionStatus=1
        else:
            print "++++++++++++ERROR submitting, will retry"
            print "Trial : "+str(i)+" / "+str(nbtrials)
            print "stderr : ",stderr
            print "stderr : ",len(stderr)

            time.sleep(10)

            
        if submissionStatus==1:
            return 1
        
        if i==nbtrials-1:
            print "failed sumbmitting after: "+str(nbtrials)+" trials, will exit"
            return 0


#__________________________________________________________
if __name__=="__main__":
    Dir = os.getcwd()
    
    user=os.environ['USER']

    import argparse
    simparser = argparse.ArgumentParser()
    simparser.add_argument("--bFieldOff", action='store_true', help="Switch OFF magnetic field (default: B field ON)")

    simparser.add_argument('-n','--numEvents', type=int, help='Number of simulation events per job', required=True)
    simparser.add_argument('-N','--numJobs', type=int, default = 10, help='Number of jobs to submit')
    simparser.add_argument('--jobOptions', type=str, default = 'config/geantSim.py', help='Name of the job options run by FCCSW (default config/geantSim.py')
    simparser.add_argument('-o','--output', type=str, help='Path of the output on EOS', required=True)

    genTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Type of events to generate
    genTypeGroup.add_argument("--singlePart", action='store_true', help="Single particle events")
    genTypeGroup.add_argument("--physics", action='store_true', help="Physics even run with Pythia")
    genTypeGroup.add_argument("--LHE", action='store_true', help="LHE events + Pythia")

    from math import pi
    singlePartGroup = simparser.add_argument_group('Single particles')
    import sys
    singlePartGroup.add_argument('-e','--energy', type=int, required = '--singlePart' in sys.argv, help='Energy of particle in GeV')
    singlePartGroup.add_argument('--etaMin', type=float, default=0., help='Minimal pseudorapidity')
    singlePartGroup.add_argument('--etaMax', type=float, default=0., help='Maximal pseudorapidity')
    singlePartGroup.add_argument('--phiMin', type=float, default=0, help='Minimal azimuthal angle')
    singlePartGroup.add_argument('--phiMax', type=float, default=2*pi, help='Maximal azimuthal angle')
    singlePartGroup.add_argument('--particle', type=int,  required = '--singlePart' in sys.argv, help='Particle type (PDG)')

    physicsGroup = simparser.add_argument_group('Physics','Physics process')
    lhe_physics = ["ljets","t","Wqq","Zqq","Hbb"]
    SM_physics = ["minBias","Haa","Zee"]
    physicsGroup.add_argument('--process', type=str, required = '--physics' in sys.argv, help='Process type', choices = lhe_physics + SM_physics)
    physicsGroup.add_argument('--pt', type=int,
                              required = ('ljets' in sys.argv or 'top' in sys.argv or 'Wqq' in sys.argv
                                          or 'Zqq' in sys.argv or 'Hbb' in sys.argv),
                              help='Transverse momentum of simulated jets (valid only for Hbb, Wqq, Zqq, t, ljet)')
    simargs, _ = simparser.parse_known_args()
    print 'ljets' in sys.argv
    print 'top' in sys.argv
    print 'Wqq' in sys.argv
    print 'Zqq' in sys.argv

    batchGroup = simparser.add_mutually_exclusive_group(required = True) # Where to submit jobs
    batchGroup.add_argument("--lsf", action='store_true', help="Submit with LSF")
    batchGroup.add_argument("--condor", action='store_true', help="Submit with condor")

    lsfGroup = simparser.add_argument_group('Pythia','Common for min bias and LHE')
    lsfGroup.add_argument('-q', '--queue', type=str, default='8nh', help='lxbatch queue (default: 8nh)')

    simargs, _ = simparser.parse_known_args()

    print "=================================="
    print "==      GENERAL SETTINGS       ==="
    print "=================================="
    magnetic_field = not simargs.bFieldOff
    b_field_str = "bFieldOn" if not simargs.bFieldOff else "bFieldOff"
    num_events = simargs.numEvents
    num_jobs = simargs.numJobs
    job_options = simargs.jobOptions
    output_path = simargs.output
    print "B field: ", magnetic_field
    print "number of events = ", num_events
    print "output path: ", output_path
    if simargs.singlePart:
        energy = simargs.energy
        etaMin = simargs.etaMin
        etaMax = simargs.etaMax
        phiMin = simargs.phiMin
        phiMax = simargs.phiMax
        pdg = simargs.particle
        particle_human_names = {11: 'electron', -11: 'positron', -13: 'mup', 13: 'mum', 22: 'photon', 111: 'pi0', 211: 'pip', -211: 'pim', 130: "K0L"}
        print "=================================="
        print "==       SINGLE PARTICLES      ==="
        print "=================================="
        print "particle PDG, name: ", pdg, " ", particle_human_names[pdg]
        print "energy: ", energy, "GeV"
        import decimal
        if etaMin == etaMax:
            print "eta: ", etaMin
            eta_str = "eta" + str(decimal.Decimal(str(etaMin)).normalize())
        else:
            print "eta: from ", etaMin, " to ", etaMax
            if abs(etaMin) == etaMax:
                eta_str = "etaTo" + str(decimal.Decimal(str(etaMax)).normalize())
            else:
                eta_str = "etaFrom" + str(decimal.Decimal(str(etaMin)).normalize()).replace('-','M') + "To" + str(decimal.Decimal(str(etaMax)).normalize()).replace('-','M')
        if phiMin == phiMax:
            print "phi: ", phiMin
            eta_str += "_phi" + str(decimal.Decimal(str(phiMin)).normalize())
        else:
            print "phi: from ", phiMin, " to ", phiMax
            if not(phiMin == 0 and phiMax == 2*pi):
                eta_str += "_phiFrom" + str(decimal.Decimal(str(phiMin)).normalize()).replace('-','M') + "To" + str(decimal.Decimal(str(phiMax)).normalize()).replace('-','M')
        job_dir = "singlePart/" + particle_human_names[pdg] + "/" + b_field_str + "/" + eta_str + "/" + str(energy) + "GeV/" 
    elif simargs.physics:
        print "=================================="
        print "==           PHYSICS           ==="
        print "=================================="
        process = simargs.process
        print "proceess: ", process
        job_dir = "physics/" + process + "/" + b_field_str + "/"
        if process in lhe_physics:
            LHE = True
            pt = simargs.pt
            print "LHE: ", LHE
            print "jet pt: ", pt
            job_dir += "etaTo1.5/" + str(pt) + "GeV/"
        else:
            job_dir += "etaFull/"
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

    # first make sure the output path exists
    outdir = output_path + "/v01/" + job_dir + "/sim/"
    print "Output will be stored in ... ", outdir 
    os.system("mkdir -p %s"%outdir)
    

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
