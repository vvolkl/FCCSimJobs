#!/usr/bin/env python2

"""
Single Particle Samples for a study of the crmc physics list.
"""

import jinja2
import os
import uuid

templates = {}
templates['condor.sub'] = """
executable            = {{jobname}}_run.sh {{env["PWD"]}}/{{submitdir}}/{{jobname}}_config.py
arguments             = $(ClusterID) $(ProcId)
output                = job.crmc.$(ClusterId).$(ProcId).out
log                   = job.crmc.$(ClusterId).$(ProcId).log
error                 = job.crmc.$(ClusterId).$(ProcId).err
RequestCpus = 8
+JobFlavour = nextweek
queue 1


"""

templates['run.sh'] = """
#!/bin/bash

export jobid={{jobid}}
export JOBDIR=$PWD
export CRMCROOT=/afs/cern.ch/work/v/vavolkl/public/fcc.cern.ch/sw/geant4-epos/x86_64-slc6-gcc62-opt/
source /cvmfs/fcc.cern.ch/sw/views/releases/externals/94.0.0/x86_64-slc6-gcc62-opt/setup.sh
cd $JOBDIR
$CRMCROOT/run fccrun.py $1
xrdcp $JOBDIR/output.root root://eospublic.cern.ch//eos/experiment/fcc/hh/simulation/samples/CRMCStudy/RUN01_debug/{{physicslist}}/events_${1/_config.py/.root}
rm $JOBDIR/output.root
"""


templates['config.py'] = """
import sys
from FCCCrmcConf.pgun_ftfp_bert import *

{%- if physicslist == "FTFP_BERT_EPOS" %}
from Configurables import SimG4FtfpBertCRMC
geant_physics_list = SimG4FtfpBertCRMC("PhysicsListEPOS")
geantservice.physicslist = geant_physics_list
{%- endif %}

ApplicationMgr().EvtMax = 20
out.filename = "output.root"

"""

runid = uuid.uuid4().hex[:7]
runname = "RUN"+runid
submitdir = "./SubmitArea"


conf = {
    'env': os.environ,
    'runid': runid,
  }

if not os.path.isdir(submitdir):
  os.makedirs(submitdir)



condor_dagfilename = submitdir + '/'+ runname +  '_sweep.dag'
print "create condor dag file " + condor_dagfilename +  "..."
condor_dagfile = open(condor_dagfilename, 'w')

for numjobs in range(100):
  for physicslist in ["FTFP_BERT_EPOS", "FTFP_BERT"]:
    conf["physicslist"] = physicslist
    jobid = uuid.uuid4().hex[:7] 
    jobname = runname + "JOB" + jobid
    conf["jobid"] = jobid
    conf["jobname"] = jobname
    print "creating files for job " + jobname
    for templatename in templates:
      t = jinja2.Template(templates[templatename])
      rendered_t = t.render(**conf)
      _filename = submitdir + "/" + jobname + "_" + templatename
      with open( _filename, 'w') as f:
        f.write(rendered_t)
      if ".sub" in templatename:
        condor_dagfile.write('JOB job%s %s\n' % (jobid, _filename))
      if ".sh" in templatename:
        os.chmod(_filename, 0755)



print "Template creation finished. Submit this set of jobs to condor with "
print "========================"
print "   condor_submit_dag " + condor_dagfilename 
print "======================="
  

