

from Configurables import SimG4SaveParticleHistory
savehisttool = SimG4SaveParticleHistory("saveHistory")
savehisttool.mcParticles.Path = "SimParticles"
savehisttool.genVertices.Path = "SimVertices"

# set up output tools for included detectors
# the algorithm itself is configured in the sim file
from Configurables import SimG4Alg
geantsim = SimG4Alg("SimG4Alg")
geantsim.outputs += [savehisttool]
