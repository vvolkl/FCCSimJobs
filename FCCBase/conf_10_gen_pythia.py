
import os

from Gaudi.Configuration import *;
from Configurables import ApplicationMgr
from GaudiKernel import SystemOfUnits as units

from Configurables import GaussSmearVertex
smeartool = GaussSmearVertex()
smeartool.xVertexSigma =   0.5*units.mm
smeartool.yVertexSigma =   0.5*units.mm
smeartool.zVertexSigma =  40.0*units.mm
smeartool.tVertexSigma = 180.0*units.picosecond

from Configurables import PythiaInterface
pythia8gentool = PythiaInterface()
path_to_pythiafile = os.environ.get("FCC_PYTHIACARDS", "")
pythiafile = os.path.join(path_to_pythiafile, 'Pythia_standard.cmd')
pythia8gentool.Filename=pythiafile

### PYTHIA algorithm
from Configurables import GenAlg
pythia8gen = GenAlg()
pythia8gen.SignalProvider = pythia8gentool
pythia8gen.VertexSmearingTool = smeartool
pythia8gen.hepmc.Path = "hepmc"
ApplicationMgr().TopAlg += [pythia8gen]

from Configurables import HepMCToEDMConverter
hepmc_converter = HepMCToEDMConverter("Converter")
hepmc_converter.hepmc.Path="hepmc"
hepmc_converter.hepmcStatusList = [] # convert particles with all statuses
hepmc_converter.genparticles.Path="GenParticlesAll"
hepmc_converter.genvertices.Path="GenVertices"
ApplicationMgr().TopAlg += [hepmc_converter]

### Filters generated particles
from Configurables import GenParticleFilter
genfilter = GenParticleFilter()
# accept is a list of particle statuses that should be accepted
genfilter.accept=[1]
genfilter.allGenParticles.Path = "GenParticlesAll"
genfilter.filteredGenParticles.Path = "GenParticles"
ApplicationMgr().TopAlg += [genfilter]


