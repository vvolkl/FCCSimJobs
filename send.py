
#python send.py -n 100 -e 10 -q 1nh -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_combinedCalo_pythia_diffCellDigitisation.py -c $PDW/PythiaCards/pythia_pp_DrellYann.cmd -o /eos/experiment/fcc/users/h/helsens/Calosim/BarrelCalo/Field/DrellYann/

#python send.py -n 100 -e 10 -q 1nh -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calocells.py -c PythiaCards/pythia_pp_DrellYann.cmd -o /eos/experiment/fcc/users/h/helsens/Calosim/BarrelCalo/NoField/DrellYann/

#for MB simulation
#python send.py -n 100 -e 500 -q 1nd -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calohits.py -c /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/PythiaCards/pythia_pp_MinBias.cmd -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/minbias/

#For MB mixing
#python send.py -n 100 -e 100 -q 8nh -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calocells_pileup.py -c /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/PythiaCards/pythia_ee_Znunu.cmd -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/100PU/

#For jets
#python send.py -n 100 -e 100 -q 8nh -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calocells.py -c /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/PythiaCards/pythia_pp_LHE.cmd -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/20GeV/ -p -j 20

#############################
#For Higgs
#python send.py -n 10 -e 50 -q 1nd -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calocells.py -c /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/PythiaCards/pythia_pp_LHE_Hbb.cmd -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diH/500GeV/SIMU/ -p -j 500 -P H

#For Z bosons
#python send.py -n 10 -e 50 -q 1nd -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calocells.py -c /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/PythiaCards/pythia_pp_LHE_Zqq.cmd -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diZ/500GeV/SIMU/ -p -j 500 -P Z

#For W bosons
#python send.py -n 10 -e 50 -q 1nd -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calocells.py -c /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/PythiaCards/pythia_pp_LHE_Wqq.cmd -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diW/500GeV/SIMU/ -p -j 500 -P W

#For top 
#python send.py -n 10 -e 50 -q 1nd -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_trackerhits_calocells.py -c /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/PythiaCards/pythia_pp_LHE_Wqq.cmd -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/ditop/500GeV/SIMU/ -p -j 500 -P top


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

    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option ('-n','--njobs', help='Number of jobs to submit',
                       dest='njobs',
                       default='10')

    parser.add_option ('-e', '--events',  help='Number of event per job. default is 100',
                       dest='events',
                       default='100')

    parser.add_option ('-q', '--queue',  help='lxbatch queue, default 8nh',
                       dest='queue',
                       default='8nh')

    parser.add_option ('-s', '--script',  help='script to be run by FCCSW',
                       dest='script',
                       default=None)

    parser.add_option ('-c', '--card',  help='pythia card',
                       dest='card',
                       default='pythia_pp_DrellYann.cmd')

    parser.add_option ('-o', '--outputeos',  help='eos output',
                       dest='outputeos',
                       default='')

    parser.add_option ('-p', '--produceLHE',  help='produceLHE flag',
                       dest='produceLHE',action='store_true')

    parser.add_option ('-j', '--jetpt',  help='jet pt',
                       dest='pt',default='20')

    parser.add_option ('-P', '--process',  help='physics process: ljets top W Z H',
                       dest='process',
                       default='ljets')


    (options, args) = parser.parse_args()
    njobs      = int(options.njobs)
    events     = int(options.events)
    script     = options.script
    queue      = options.queue
    card       = options.card
    outputeos  = options.outputeos
    produceLHE = options.produceLHE
    process    = options.process
    pt         = int(options.pt)
    rundir = os.getcwd()
    nbjobsSub=0

    for i in xrange(njobs):
        seed = int(datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
        uniqueID='%s_%i'%(user,seed)
        
        logdir=Dir+"/BatchOutputs/"
        os.system("mkdir -p %s"%logdir)
        cardname=card.split('/')[-1]
        frunname = 'job_%s_%s.sh'%(cardname.replace('.cmd',''),uniqueID)
        outfile = 'output_%s.root'%(uniqueID)
        outfileconv = outfile.replace('.root','_converted.root')

        frun = None
        try:
            frun = open(logdir+'/'+frunname, 'w')
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            time.sleep(10)
            frun = open(logdir+'/'+frunname, 'w')


        commands.getstatusoutput('chmod 777 %s/%s'%(logdir,frunname))
        frun.write('#!/bin/bash\n')
        frun.write('unset LD_LIBRARY_PATH\n')
        frun.write('unset PYTHONHOME\n')
        frun.write('unset PYTHONPATH\n')
        frun.write('export JOBDIR=$PWD\n')
        frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/\n')
        frun.write('source ./init.sh\n')
        frun.write('export EOS_MGM_URL=\"root://eospublic.cern.ch\"\n')

        if produceLHE:
            frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Generators/FlatGunLHEventProducer\n')

            if process=='ljets':
                frun.write('python flatGunLHEventProducer.py   --pdg 1 2 3   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(events,pt,pt,seed))
            elif process=='bjets':
                frun.write('python flatGunLHEventProducer.py   --pdg 5   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(events,pt,pt,seed))
            elif process=='top':
                frun.write('python flatGunLHEventProducer.py   --pdg 6   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(events,pt,pt,seed))
            elif process=='Z':
                frun.write('python flatGunLHEventProducer.py   --pdg 23   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(events,pt,pt,seed))
            elif process=='W':
                frun.write('python flatGunLHEventProducer.py   --pdg 24   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(events,pt,pt,seed))
            elif process=='H':
                frun.write('python flatGunLHEventProducer.py   --pdg 25   --guntype pt   --nevts %i   --ecm 100000.   --pmin %f   --pmax %f   --etamin -1.4   --etamax 1.4  --seed %i   --output $JOBDIR/events.lhe\n'%(events,pt,pt,seed))
            else:
                print 'process does not exists, exit'
                sys.exit(3)
            frun.write('gunzip $JOBDIR/events.lhe.gz\n')
            frun.write('cp %s $JOBDIR/card.cmd\n'%(card))
            frun.write('echo "Beams:LHEF = $JOBDIR/events.lhe" >> $JOBDIR/card.cmd\n')
            frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/\n')
            frun.write('./run fccrun.py  %s  --outputfile=$JOBDIR/%s --nevents=%i --inputfile=$JOBDIR/card.cmd\n'%(script, outfile ,events))

        else:
            frun.write('./run fccrun.py  %s  --outputfile=$JOBDIR/%s --nevents=%i --inputfile=%s\n'%(script, outfile ,events, card))

        frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/\n')
        frun.write('python eoscopy.py $JOBDIR/%s %s\n'%(outfile,outputeos))

        cmdBatch="bsub -M 4000000 -R \"pool=40000\" -q %s -cwd%s %s" %(queue, logdir,logdir+'/'+frunname)
        batchid=-1
        job,batchid=SubmitToBatch(cmdBatch,10)
        nbjobsSub+=job

    print 'succesfully sent %i  jobs'%nbjobsSub
