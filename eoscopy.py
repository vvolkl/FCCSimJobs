import glob, os, sys,subprocess
import time
#__________________________________________________________
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}


#__________________________________________________________
if __name__=="__main__":
    if len(sys.argv)!=3:
        print 'usage python eoscopy infile outeos'
        sys.exit(3)
    infile=sys.argv[1]
    outfile=sys.argv[2]
    nbtrials=10
    cmd = 'cp %s %s'%(infile,outfile)

    for i in range(nbtrials):            
        outputCMD = getCommandOutput(cmd)
        stderr=outputCMD["stderr"].split('\n')

        for line in stderr :
            if line=="":
                print "------------GOOD COPY"
                submissionStatus=1
                break
            else:
                print "++++++++++++ERROR copying, will retry"
                print "error: ",stderr
                print "Trial : "+str(i)+" / "+str(nbtrials)
                time.sleep(10)
                break

        if submissionStatus==1:
            break
        
        if i==nbtrials-1:
            print "failed sumbmitting after: "+str(nbtrials)+" trials, will exit"
            break
