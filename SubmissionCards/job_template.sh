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

