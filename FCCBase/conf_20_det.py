

import os
from Gaudi.Configuration import *


from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc")
# if FCC_DETECTORS is empty, this should use relative path to working directory
path_to_detector = os.environ.get("FCC_DETECTORS", "")
detectors_to_use=[
                    'Detector/DetFCChhBaseline1/compact/FCChh_DectMaster.xml',
                  ]
# prefix all xmls with path_to_detector
geoservice.detectors = [os.path.join(path_to_detector, _det) for _det in detectors_to_use]
geoservice.OutputLevel = WARNING
ApplicationMgr().ExtSvc += [geoservice]

geant_output_tool_list = []

from Configurables import SimG4SaveParticleHistory
savehisttool = SimG4SaveParticleHistory("saveHistory")
savehisttool.mcParticles.Path = "SimParticles"
savehisttool.genVertices.Path = "SimVertices"
geant_output_tool_list += [savehisttool]

from Configurables import SimG4SaveTrackerHits
savetrackertool = SimG4SaveTrackerHits("saveTrackerHits")
savetrackertool.readoutNames = [
                                "TrackerBarrelReadout", 
                                "TrackerEndcapReadout",
                                ]
savetrackertool.positionedTrackHits.Path = "TrackerHitsPosition"
savetrackertool.trackHits.Path = "TrackerHits"
savetrackertool.digiTrackHits.Path = "TrackerHitsDigiPostPoint"
geant_output_tool_list += [savetrackertool]

calo_readouts = {
                  "EcalBarrel": ["ECalBarrelEta"],
                  "HcalBarrel": ["HCalBarrelReadout"],
                  #"MiscCalo":   [
                  #                "ECalBarrelPhiEta",
                  #                "EMECPhiEta",
                  #                "EMFwdPhiEta",
                  #                "HCalExtBarrelReadout",
                  #                "HECPhiEta",
                  #                "HFwdPhiEta",
                  #                "Muons_Readout",
                  #              ]
                  }



from Configurables import SimG4SaveCalHits
for calo_name in calo_readouts:
  savecaltool = SimG4SaveCalHits(calo_name)
  savecaltool.readoutNames = calo_readouts[calo_name]
  savecaltool.positionedCaloHits.Path = calo_name + "HitsPositions"
  savecaltool.caloHits.Path = calo_name + "Hits"
  geant_output_tool_list += [savecaltool]



# set up output tools for included detectors
# the algorithm itself is configured in the sim file
from Configurables import SimG4Alg
geantsim = SimG4Alg("SimG4Alg")
geantsim.outputs += geant_output_tool_list
