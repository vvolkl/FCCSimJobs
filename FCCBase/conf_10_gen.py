
from Gaudi.Configuration import *;

from Configurables import ApplicationMgr
from GaudiKernel import SystemOfUnits as units

from Configurables import GaussSmearVertex
smeartool = GaussSmearVertex()
smeartool.xVertexSigma =   0.5*units.mm
smeartool.yVertexSigma =   0.5*units.mm
smeartool.zVertexSigma =  40.0*units.mm
smeartool.tVertexSigma = 180.0*units.picosecond

from Configurables import  ConstPtParticleGun
pgun_tool = ConstPtParticleGun()
pgun_tool.PdgCodes = [11, 13]
pgun_tool.PhiMin = 0.3343

from Configurables import GenAlg
genalg_pgun = GenAlg()
genalg_pgun.SignalProvider =  ConstPtParticleGun('ToolSvc.ConstPtParticleGun')
genalg_pgun.VertexSmearingTool = smeartool
genalg_pgun.hepmc.Path = "hepmc"
ApplicationMgr().TopAlg += [genalg_pgun]

from Configurables import HepMCToEDMConverter
hepmc_converter = HepMCToEDMConverter()
hepmc_converter.hepmc.Path="hepmc"
hepmc_converter.genparticles.Path="GenParticlesAll"
hepmc_converter.genvertices.Path="GenVertices"
ApplicationMgr().TopAlg += [hepmc_converter]

from Configurables import GenParticleFilter
### Filters generated particles
# accept is a list of particle statuses that should be accepted
genfilter = GenParticleFilter("StableParticleFilter")
genfilter.accept = [1]
genfilter.allGenParticles.Path = "GenParticlesAll"
genfilter.filteredGenParticles.Path = "GenParticles"
ApplicationMgr().TopAlg += [genfilter]
