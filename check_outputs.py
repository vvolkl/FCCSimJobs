#python check_outputs.py /eos/experiment/fcc/hh/simulation/samples/v01
import glob, os, sys,subprocess,cPickle
import commands
import time
import random
from datetime import datetime
import ROOT as r
import json
import warnings

outname='/afs/cern.ch/work/h/helsens/public/FCCDicts/SimulationDict_v01.json'
if not os.path.exists(outname):
    file_handle = open(outname,"w")
    file_handle.write('{}\n')
    file_handle.close()

mydict=None
with open(outname) as f:
    mydict = json.load(f)


#__________________________________________________________
def jobexits(uid,jobid):
        if len(mydict)==0:return False
        for s in mydict:
            if s==uid: 
                for j in mydict[uid]:
                    if jobid==j['jobid']: return True
        return False

#__________________________________________________________
def addfile(uid,nevents,jobid, out, status):
        if jobexits(uid,jobid): 
            print 'job already exist ',uid,'   ',jobid
            return
        exist=False
        for s in mydict:
            if s==uid: 
                exist=True
                mydict[uid].append({'jobid':jobid,'nevents':nevents,'out':out,'status':status})
        if not exist:
            mydict[uid]=[{'jobid':jobid,'nevents':nevents,'out':out,'status':status}]
        return


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
def checkFile(f, tname):
    tf=None
    try:
        tf=r.TFile.Open(f)
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ValueError:
        print "Could read the file"
    except:
        print "Unexpected error:", sys.exc_info()[0]
        print 'file ===%s=== must be deleted'%f
        #os.system('rm %s'%f)
        return False

    tf=r.TFile.Open(f)
    tt=None
    try :
        tt=tf.Get(tname)
        if tt==None:
            print 'file ===%s=== must be deleted'%f
            #os.system('rm %s'%f)
            return False

    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ValueError:
        print "Could read the file"
    except:
        print "Unexpected error:", sys.exc_info()[0]
        print 'file ===%s=== must be deleted'%f
        #os.system('rm %s'%f)
        return False
    

    with warnings.catch_warnings(record=True) as was:
        f=r.TFile.Open(f)
        ctrlstr = 'probably not closed'
        for w in was:
            if ctrlstr in str(w.message):
                #os.system('rm %s'%f)
                return False
    
    f=r.TFile.Open(f)
    tt=tf.Get(tname)
    if tt.GetEntries()==0:
        print 'file has 0 entries ===%s=== must be deleted'%f
        return False


    return True
#__________________________________________________________
if __name__=="__main__":


    basedir=sys.argv[1]
    ldir=[x[0] for x in os.walk(basedir)]
    ldirsmall=[x.replace(basedir,'') for x in ldir]
    #ldir=os.walk(basedir)


    for l in ldir:
        uid=l.replace("/eos/experiment/fcc/hh/simulation/samples/","")
        #uid=uid.replace("/","_")

        All_files = glob.glob("%s/*.root"%(l))
        if len(All_files)==0:continue
        key=l.replace(basedir,'').replace('/','_')
        print key
        
        ntot=0
        for i in xrange(len(All_files)):
            if os.path.isfile(All_files[i]):
                print '-----------',All_files[i]
                jobid=All_files[i].split('_')[-1]
                jobid=jobid.replace('.root','')
                if '/simu/' in All_files[i] or  '/SIMU/' in All_files[i]:
                    if not checkFile(All_files[i], 'events'):
                        addfile(uid,nevents,jobid, All_files[i],'BAD')
                        continue
                    tf=r.TFile.Open(All_files[i])
                    tt=tf.Get('events')
                    nevents=tt.GetEntries()
                    ntot+=nevents
                    addfile(uid,nevents,jobid, All_files[i],'DONE')
                elif '/ntup/' in All_files[i]:
                    if not checkFile(All_files[i], 'ana/hgc'):
                        addfile(uid,nevents,jobid, All_files[i],'BAD')
                        continue
                    tf=r.TFile.Open(All_files[i])
                    tt=tf.Get('ana/hgc')
                    nevents=tt.GetEntries()
                    ntot+=nevents
                    addfile(uid,nevents,jobid, All_files[i],'DONE')
                else:
                    print 'not correct'
        print ntot
    

    with open(outname, 'w') as f:
        json.dump(mydict, f)
        

