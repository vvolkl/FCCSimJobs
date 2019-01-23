

import os
from Gaudi.Configuration import *

path_to_detector = os.environ("FCCDETECTORS") + '/'


detectors_to_use=[
                    path_to_detector+'Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                    path_to_detector+'Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                  ]

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc")
geoservice.detectors = detectors_to_use
geoservice.OutputLevel = WARNING
ApplicationMgr().ExtSvc += [geoservice]

geant_output_tool_list = []


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


# set up output tools for included detectors
# the algorithm itself is configured in the sim file
from Configurables import SimG4Alg
geantsim = SimG4Alg("SimG4Alg")
geantsim.outputs += geant_output_tool_list
