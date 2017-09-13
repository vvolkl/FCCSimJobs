# FCCGunLHE
[]() Clone and initialisation
-------------------------

If you do not attempt to contribute to the repository, simply clone it:
```
git clone git@github.com:clementhelsens/FCCGunLHE.git
```

If you aim at contributing to the repository, you need to fork and then clone the forked repository:
```
git clone git@github.com:YOURGITUSERNAME/FCCGunLHE.git
```

[]() Sending simulation jobs
-------------------------
```
python send.py -n 100 -e 10 -q 1nh -s /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/Reconstruction/RecCalorimeter/tests/options/geant_fullsim_combinedCalo_pythia_diffCellDigitisation.py -c PythiaCards/pythia_pp_DrellYann.cmd -o /eos/experiment/fcc/users/h/helsens/Calosim/BarrelCalo/Field/DrellYann/
```