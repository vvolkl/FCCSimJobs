# README of using FCCSimJobs for single pion analysis in FCC-hh reference detector -- for CDR summary
# General remarks: 
# - use the --resegmentHCal flag to use HCalBarrel segmentation of DeltaEta=0.025, otherwise high-granularity option is used
# - use the --benchmark flag to calibrate the topo-clusters according to the benchmark method, if not used the clusters are calibrated on EM scale


# Simulation of single pions
# for energy X, 100ev per job, 100 jobs, eta=0.36, B=4T:
python python/send.py --singlePart --particle -211 -e X --etaMin 0.36 --etaMax 0.36 -n 100 -N 100 --condor

# use topo-clustering for energy reconstruction, electronics noise considered:
python python/send.py --singlePart --particle -211 -e X --etaMin 0.36 --etaMax 0.36 -n -1 -N 100 --condor --local inits/reco.py  --recTopoClusters (--resegmentHCal) --noise

# to use the benchmark cluster calibration add --benchmark:
python python/send.py --singlePart --particle -211 -e X --etaMin 0.36 --etaMax 0.36 -n -1 -N 100 --condor --local inits/reco.py  --recTopoClusters (--resegmentHCal) --noise --benchmark

# Study PU scenarios:
# First 2 steps described in FCCSimJobs documentation.
# 1. step: simulation of enough minimum bias events.
# 2. step: merge min bias events to PU = 200 scenario:
python python/send.py --physics --process MinBias -n 10 -N 1 --condor --local inits/reco.py --mergePileup --pileup 200

# 3. step: overlay PU = 200 scenario with signal:
python python/send.py --singlePart --particle -211 -e X --etaMin 0.36 --etaMax 0.36 -n -1 -N 100 --condor --local inits/reco.py --addPileupToSignal --pileup 200 --rebase (--resegmentHCal)

# 4. step: run topo-cluster reconstruction on single pions in PU = 200 scenario:
python python/send.py --singlePart --particle -211 -e X --etaMin 0.36 --etaMax 0.36 -n -1 -N 100 --condor --local inits/reco.py --recTopoClusters (--resegmentHCal) --pileup 200 --rebase --noise (--benchmark)