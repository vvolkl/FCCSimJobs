
#python send.py -n 100 -e 10 -q 1nh -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_combinedCalo_pythia_diffCellDigitisation.py -c PythiaCards/pythia_pp_DrellYann.cmd -o /eos/experiment/fcc/users/h/helsens/Calosim/BarrelCalo/Field/DrellYann/
#python send.py -n 100 -e 10 -q 1nh -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_combinedCalo_pythia_diffCellDigitisation_noField.py -c PythiaCards/pythia_pp_DrellYann.cmd -o /eos/experiment/fcc/users/h/helsens/Calosim/BarrelCalo/NoField/DrellYann/

import glob, os, sys,subprocess,cPickle
import commands
import time
import random
import datetime


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
    
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    user=os.environ['USER']
    uniqueID='%s_%s'%(user,st)

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


    (options, args) = parser.parse_args()
    njobs      = int(options.njobs)
    events     = int(options.events)
    script     = options.script
    queue      = options.queue
    card       = options.card
    outputeos  = options.outputeos
    rundir = os.getcwd()
    nbjobsSub=0

    for i in xrange(njobs):
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
        frun.write('./run fccrun.py  %s  --outputfile=$JOBDIR/%s --nevents=%i --inputfile=%s\n'%(script, outfile ,events, card))
        frun.write('python Convert.py $JOBDIR/%s $JOBDIR/%s\n'%(outfile,outfileconv))
        frun.write('python eoscopy.py $JOBDIR/%s %s\n'%(outfile,outputeos))
        frun.write('python eoscopy.py $JOBDIR/%s %s\n'%(outfileconv,outputeos))

        cmdBatch="bsub -M 2000000 -R \"rusage[pool=2000]\" -q %s -cwd%s %s" %(queue, logdir,logdir+'/'+frunname)
        batchid=-1
        job,batchid=SubmitToBatch(cmdBatch,10)
        nbjobsSub+=job

    print 'succesfully sent %i  jobs'%nbjobsSub
