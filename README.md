# FCCGunLHE
[]() Clone and initialisation
-------------------------

If you do not attempt to contribute to the repository, simply clone it:
```
git clone git@github.com:clementhelsens/FCCSimJobs.git
```

If you aim at contributing to the repository, you need to fork and then clone the forked repository:
```
git clone git@github.com:YOURGITUSERNAME/FCCSimJobs.git
```

[]() Sending simulation jobs
-------------------------
Various options are available and are explained below. 
First if **--singlePart** is used, the following options are possible:
   - **--particle** for the particle ID. The supported ones are 11(e-), -11(e+), -13(mu-), 13(mu+), 22, 111(pi0), 211(pi+), -211(pi-), 130(K0L). For example to run single anti-muon, use **--particle -13**
   - the angle is changed using **--phiMin** and **--phiMax**, default are 0 and 2pi respectively
Second if **--physics** is used, the following options are possible
   - **--process** to select the type of process. Two types are available
      - from LHE events, this will call a gun that will produce 2 back to back objects, the following keys are available **ljets**, **top**, **Wqq**, **Zqq**, **Hbb**. If this option is used, the pt can also be given using **--pt**
      - from calling pythia8 direcly, thus generating the events at 100TeV, the following keys are available **MinBias**, **Haa**, **Zee**, **H4e**
Third there are common options
   - the pseudo-rapidity range is changed using **--etaMin** and **--etaMax**, default is 0 for both 
   - the batch system is either **--lsf**  or **--condor**
   - the number of events per job is configured through **-n**
   - and the number of jobs to send is configured through **-N**
   
```
python send.py --singlePart --particle -211 -e 10 -n 10 -N 1 --condor
python send.py --physics --process Zqq --pt 1000 -n 10 -N 1 --lsf
```
Also, please often check the afs directory where the jobs where send


[]() Checking the results
-------------------------
