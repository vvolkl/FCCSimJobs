

import os
from Gaudi.Configuration import *

path_to_detector = os.environ("FCCDETECTORS") + '/'


detectors_to_use=[
                    path_to_detector+'Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                    path_to_detector+'Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                    path_to_detector+'/Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                    path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml',
                    path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalExtendedBarrel_TileCal.xml',
                    path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml',
                    path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Forward_coneCryo.xml',
                    path_to_detector+'/Detector/DetFCChhTailCatcher/compact/FCChh_TailCatcher.xml',
                    path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Solenoids.xml',
                    path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Shielding.xml',
                  ]

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc")
geoservice.detectors = detectors_to_use
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
