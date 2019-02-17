import sys
from FCCCrmcConfig.pgun_ftfp_bert import *

from Configurables import SimG4FtfpBertCRMC
geant_physics_list = SimG4FtfpBertCRMC("PhysicsListEPOS")
geantservice.physicslist = geant_physics_list

ApplicationMgr().EvtMax = 2
out.filename = sys.argv[1]


