
from Gaudi.Configuration import *
from GaudiKernel import SystemOfUnits as units


from Configurables import SimG4FullSimActions
actions = SimG4FullSimActions()
actions.enableHistory=True

from Configurables import SimG4ConstantMagneticFieldTool
field = SimG4ConstantMagneticFieldTool("bField")
field.FieldOn = True
field.FieldZMax = 20*units.m
field.IntegratorStepper = "ClassicalRK4"

from Configurables import SimG4DD4hepDetector
geant_detector_tool = SimG4DD4hepDetector("SimG4DD4hepDetector")

from Configurables import SimG4FtfpBert
geant_physics_list = SimG4FtfpBert("PhysicsList")

from Configurables import SimG4Svc
geantservice = SimG4Svc("SimG4Svc")
geantservice.detector = geant_detector_tool
geantservice.physicslist = geant_physics_list
geantservice.actions = actions
geantservice.magneticField = field
# range cut
geantservice.g4PostInitCommands += ["/run/setCut 0.1 mm"]
ApplicationMgr().ExtSvc +=  [geantservice]



geant_output_tool_list = []

# ouput tools are configured in the detector config

from Configurables import SimG4SaveParticleHistory
savehisttool = SimG4SaveParticleHistory("saveHistory")
savehisttool.mcParticles.Path = "SimParticles"
savehisttool.genVertices.Path = "SimVertices"
geant_output_tool_list += [savehisttool]


from Configurables import SimG4PrimariesFromEdmTool
particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
particle_converter.genParticles.Path = "GenParticles"

from Configurables import SimG4Alg
geantsim = SimG4Alg("SimG4Alg")
geantsim.outputs = geant_output_tool_list
geantsim.eventProvider = particle_converter
main.TopAlg += [geantsim]
