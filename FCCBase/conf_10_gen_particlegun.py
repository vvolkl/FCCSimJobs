
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

from Configurables import GenAlg
genalg_pgun = GenAlg()
genalg_pgun.SignalProvider = pgun_tool 
genalg_pgun.VertexSmearingTool = smeartool
genalg_pgun.hepmc.Path = "hepmc"
ApplicationMgr().TopAlg += [genalg_pgun]

from Configurables import HepMCToEDMConverter
hepmc_converter = HepMCToEDMConverter()
hepmc_converter.hepmc.Path="hepmc"
hepmc_converter.genparticles.Path="GenParticles"
hepmc_converter.genvertices.Path="GenVertices"
ApplicationMgr().TopAlg += [hepmc_converter]

