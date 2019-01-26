
from Gaudi.Configuration import *;

from Configurables import  PythiaInterface
pythia8gentool = PythiaInterface()
pythia8gentool.Filename = "Generation/data/Pythia_minbias_pp_100TeV.cmd"

GenAlg.SignalProvider = pythia8gentool
