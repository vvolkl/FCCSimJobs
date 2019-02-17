#!/bin/bash

export JOBDIR=$PWD
export CRMCROOT=/afs/cern.ch/work/v/vavolkl/public/fcc.cern.ch/sw/geant4-epos/x86_64-slc6-gcc62-opt/
source /cvmfs/fcc.cern.ch/sw/views/releases/externals/94.0.0/x86_64-slc6-gcc62-opt/setup.sh
cd $JOBDIR
$CRMCROOT/run fccrun.py $1
xrdcp $JOBDIR/output.root root://eospublic.cern.ch//eos/experiment/fcc/hh/simulation/samples/CRMC/RUN01_debug
rm $JOBDIR/output.root

