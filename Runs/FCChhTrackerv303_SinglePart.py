#!/usr/bin/env python2

"""
Single Particle Samples for the FCChh Tracker v3.03.
"""

import jinja2
import os
import uuid

templates = {}
templates['condor.sub'] = """
{#- Set defaults for template variables #}
{#- '<1> or <2>' is a shorthand for 'if <1> is false then <2>' #}
{%- set user=user or env['user'] %}
{%- set jobdir=jobdir or env["PWD"]  %}
{%- set seed=seed or 0  %}

executable            = {{jobdir}}/{{jobscript or "test.sh"}}
arguments             = $(ClusterID) $(ProcId)
output                = {{jobdir}}/out/job.{{user}}_{{seed}}.$(ClusterId).$(ProcId).out
log                   = {{jobdir}}/log/job.{{user}}_{{seed}}.$(ClusterId).$(ProcId).log
error                 = {{jobdir}}/err/job.{{user}}_{{seed}}.$(ClusterId).$(ProcId).err
RequestCpus = {{RequestCpus or 8}}
+JobFlavour = {{JobFlavour or "nextweek"}}
queue {{queue or 1}}
"""

templates['run.sh'] = """


#!/bin/bash

{#- Set defaults for template variables #}
{#- '<1> or <2>' is a shorthand for 'if <1> is false then <2>' #}
{%- set user=user or env['user'] %}
{%- set jobdir=jobdir or env["PWD"]  %}
{%- set seed=seed or 0  %}
{%- set init_script=init_script or "/cvmfs/fcc.cern.ch/sw/views/releases/externals/94.0.0/x86_64-slc6-gcc62-opt/setup.sh" %}
{%- set fcc_runcommand=fcc_runcommand or "fccrun.py" %}
{%- set fcc_config=fcc_config or "fccsw.conf.py"  %}
{%- set fcc_config_dir=fcc_config_dir or jobdir  %}
{%- set outfile=outfile or "output.root"  %}
{%- set eos_out_dir=eos_out_dir or "/eos/experiment/fcc/hh/simulation/test"  %}

export JOBDIR=$PWD
source {{init_script}}
cd $JOBDIR
{{fcc_runcommand}} {{fcc_config_dir}}/{{fcc_config}} {{fcc_command_args or ""}}
xrdcp $JOBDIR/{{outfile}} {{eos_out_dir}}
rm $JOBDIR/{{outfile}}
}


"""

templates['config.py'] = """


#!/usr/bin/env gaudirun.py

# use common config (order is important!)
from FCCBase.conf_00_main import *
from FCCBase.conf_10_particlegun import *
# pick  and choose modules
#from FCCBase.conf_20_det import *
#from FCCBase.conf_30_sim import *
from FCCBase.conf_32_sim_randomseed import randomEngine
#from FCCBase.conf_99_ouput import *

# change a single options
randomEngine.Seeds = [4444]
# changing properties of private tools is slightly awkward
# important to do it via the algorithm that owns it
GenAlg().SignalProvider.PdgCodes = [14]

# set number of Events
ApplicationMgr().EvtMax = 12


"""

runid = uuid.uuid4().hex[:7]
runname = "RUN"+runid
submitdir = ""


conf = {
    'env': os.environ,
  }


os.makedirs(submitdir)



condor_dagfilename = submitdir + '/'+ runname +  '_sweep.dag'
print "create condor dag file " + condor_dagfilename +  "..."
condor_dagfile = open(condor_dagfilename, 'w')

for numjobs in range(3):
  jobid = uuid.uuid4().hex[:7] 
  jobname = "JOB" + jobid
  conf["jobid"] = jobid
  print "creating files for job " + jobname
  for templatename in templates:
    t = jinja2.Template(templates[templatename])
    rendered_t = t.render(**conf)
    _filename = jobname + "_" + templatename
    with open( submitdir + "/" + _filename, 'w') as f:
      f.write(rendered_t)
    if ".sub" in templatename:
      condor_dagfile.write('JOB job%s %s\n' % (jobid, _filename))


print "Template creation finished. Submit this set of jobs to condor with "
print "========================"
print "   condor_submit_dag " + condor_dagfilename 
print "======================="
  

