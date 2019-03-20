import argparse
simparser = argparse.ArgumentParser()
simparser.add_argument('--inName', type=str, help='Name of the input file', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('--detectorPath', type=str, help='Path to detectors', default = "/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj")
simparser.add_argument('--prefixCollections', type=str, help='Prefix added to the collection names', default="")
simparser.add_argument("--resegmentHCal", action='store_true', help="Merge HCal cells in DeltaEta=0.025 bins", default = False)
simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
input_name = simargs.inName
output_name = simargs.outName
path_to_detector = simargs.detectorPath
resegmentHCal = simargs.resegmentHCal
print "detectors are taken from: ", path_to_detector
print "input name: ", input_name
print "output name: ", output_name
prefix = simargs.prefixCollections
print "prefix : ", prefix
print "resegment HCal: ", resegmentHCal
print "=================================="

from Gaudi.Configuration import *

from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput

# v01 production - min. bias events
podioevent = FCCDataSvc("EventDataSvc", input=input_name)

from Configurables import PodioInput

podioinput = PodioInput("in", collections = [prefix+"ECalBarrelCells", prefix+"HCalBarrelCells"])

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = [ path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                                            path_to_detector+'/Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                                            path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml',
                                            ],
                    OutputLevel = WARNING)

# Pileup in ECal Barrel
# readout name
ecalBarrelReadoutNamePhiEta = "ECalBarrelPhiEta"
hcalBarrelReadoutName = "HCalBarrelReadout"
hcalBarrelReadoutNamePhiEta = "BarHCal_Readout_phieta"
# active material identifier name
hcalIdentifierName = ["module", "row", "layer"]
# active material volume name
hcalVolumeName = ["moduleVolume", "wedgeVolume", "layerVolume"]
# ECAL bitfield names & values 
hcalFieldNames=["system"]
hcalFieldValues=[8]

##############################################################################################################                                                                                           #######                                       CELL POSITIONS  TOOLS                              #############                                                                                           ##############################################################################################################                                                                                           # Configure tools for calo cell positions                                                                            
from Configurables import CellPositionsECalBarrelTool, CellPositionsHCalBarrelNoSegTool, CellPositionsHCalBarrelTool
ECalBcells = CellPositionsECalBarrelTool("CellPositionsECalBarrel",
                                         readoutName = ecalBarrelReadoutNamePhiEta,
                                         OutputLevel = INFO)
HCalBcellVols = CellPositionsHCalBarrelNoSegTool("CellPositionsHCalBarrelVols",
                                                 readoutName = hcalBarrelReadoutName,
                                                 OutputLevel = INFO)
HCalBsegcells = CellPositionsHCalBarrelTool("CellPositionsHCalSegBarrel",
                                            readoutName = hcalBarrelReadoutNamePhiEta,
                                            radii = [2910.5, 3010.5, 3135.5, 3285.5, 3435.5, 3585.5, 3785.5, 4135.5, 4285.5, 4535.5],
                                            OutputLevel = INFO)

##############################################################################################################                                                                                           #######                                       RESEGMENT HCAL                                   #############                                                                                             ##############################################################################################################                                                                                                                              
from Configurables import CreateVolumeCaloPositions,RedoSegmentation,CreateCaloCells,CreateCellPositions
# Create cells in HCal                                           
# 2. step - rewrite the cellId using the Phi-Eta segmentation    
# 3. step - merge new cells corresponding to eta-phi segmentation
# Hcal barrel cell positions                                                                                                                                                                             
posHcalBarrel = CreateCellPositions("posHcalBarrel",
                                    positionsTool=HCalBcellVols,
                                    hits = prefix+"HCalBarrelCells",
                                    positionedHits = "HCalBarrelPositions")

# Use Phi-Eta segmentation in Hcal barrel                       
resegmentHcalBarrel = RedoSegmentation("ReSegmentationHcal",
                                       # old bitfield (readout) 
                                       oldReadoutName = hcalBarrelReadoutName,
                                       # specify which fields are going to be altered (deleted/rewritten)
                                       oldSegmentationIds = ["module","row"],
                                       # new bitfield (readout), with new segmentation                                                                                     
                                       newReadoutName = hcalBarrelReadoutNamePhiEta,
                                       inhits = "HCalBarrelPositions",
                                       outhits = "HCalBarrelCellsStep2")
    
createHcalBarrelCells = CreateCaloCells("CreateHCalBarrelCells",
                                        doCellCalibration=False,recalibrateBaseline =False, 
                                        addCellNoise=False, filterCellNoise=False,
                                        hits="HCalBarrelCellsStep2",
                                        cells="newHCalBarrelCells")
hcalCells = prefix+"HCalBarrelCells"
hcalCellsForTowers = "HCalBarrelCellsStep2"
if resegmentHCal:
    hcalCells = "newHCalBarrelCells"
    hcalCellsForTowers = "newHCalBarrelCells"

# geometry tool
from Configurables import TubeLayerPhiEtaCaloTool, LayerPhiEtaCaloTool, NestedVolumesCaloTool
ecalBarrelGeometry = TubeLayerPhiEtaCaloTool("EcalBarrelGeo",
                                             readoutName = ecalBarrelReadoutNamePhiEta,
                                             activeVolumeName = "LAr_sensitive",
                                             activeFieldName = "layer",
                                             fieldNames = ["system"],
                                             fieldValues = [5],
                                             activeVolumesNumber = 8)
# Geometry for layer-eta-phi segmentation                                                                                           
hcalBarrelGeometry = LayerPhiEtaCaloTool("hcalBarrelGeometry",
                                         readoutName = "BarHCal_Readout_phieta",
                                         activeVolumeName = "layerVolume",
                                         activeFieldName = "layer",
                                         fieldNames = ["system"],
                                         fieldValues = [8],
                                         activeVolumesNumber = 10,
                                         activeVolumesEta = [1.2524, 1.2234, 1.1956, 1.15609, 1.1189, 1.08397, 1.0509, 0.9999, 0.9534, 0.91072]
                                         )

# No segmentation, geometry with nested volumes                                                                                                        
hcalgeo = NestedVolumesCaloTool("hcalgeo",
                                activeVolumeName = hcalVolumeName,
                                activeFieldName = hcalIdentifierName,
                                readoutName = "HCalBarrelReadout",
                                fieldNames = hcalFieldNames,
                                fieldValues = hcalFieldValues)

from Configurables import CreateEmptyCaloCellsCollection
createemptycells = CreateEmptyCaloCellsCollection("CreateEmptyCaloCells")
createemptycells.cells.Path = "emptyCaloCells"
#Create calo clusters
from Configurables import CreateCaloClustersSlidingWindow, CaloTowerTool
from GaudiKernel.PhysicalConstants import pi

towers = CaloTowerTool("towers",
                               deltaEtaTower = 0.01, deltaPhiTower = 2*pi/704.,
                               ecalBarrelReadoutName = ecalBarrelReadoutNamePhiEta,
                               ecalEndcapReadoutName = "",
                               ecalFwdReadoutName = "",
                               hcalBarrelReadoutName = hcalBarrelReadoutNamePhiEta,
                               hcalExtBarrelReadoutName = "",
                               hcalEndcapReadoutName = "",
                               hcalFwdReadoutName = "")
towers.ecalBarrelCells.Path = prefix+"ECalBarrelCells"
towers.ecalEndcapCells.Path = "emptyCaloCells"
towers.ecalFwdCells.Path = "emptyCaloCells"
towers.hcalBarrelCells.Path = hcalCellsForTowers
towers.hcalExtBarrelCells.Path = "emptyCaloCells"
towers.hcalEndcapCells.Path = "emptyCaloCells"
towers.hcalFwdCells.Path = "emptyCaloCells"

inputNoisePerCell = "/afs/cern.ch/work/c/cneubuse/public/FCChh/cellNoise_map_segHcal_electronicsNoiseLevel.root"
if resegmentHCal:
    inputNoisePerCell = "/afs/cern.ch/work/c/cneubuse/public/FCChh/cellNoise_map_electronicsNoiseLevel.root"

# use topo-cluster map of electronics noise level per Barrel cell
from Configurables import TopoCaloNoisyCells
readNoisyCellsMap = TopoCaloNoisyCells("ReadNoisyCellsMap",
                                       fileName = inputNoisePerCell)
# call pileup tool
# prepare TH2 histogram with pileup per abs(eta)
from Configurables import PreparePileup
pileupEcalBarrel = PreparePileup("PreparePileupEcalBarrel",
                                 geometryTool = ecalBarrelGeometry,
                                 readoutName = ecalBarrelReadoutNamePhiEta,
                                 layerFieldName = "layer",
                                 towerTool = towers,
                                 positionsTool = ECalBcells,
                                 noiseTool = readNoisyCellsMap,
                                 histogramName = "ecalBarrelEnergyVsAbsEta",
                                 numLayers = 8,
                                 etaSize = [7,  5,  7,   9,   3,   3,  99],
                                 phiSize = [19, 15, 21, 21,  15,  11, 101])
pileupEcalBarrel.hits.Path=prefix+"ECalBarrelCells"

hcalGeoService = hcalgeo
hcalCellPositions = HCalBcellVols
hcalReadoutName = hcalBarrelReadoutName
if resegmentHCal:
    hcalGeoService = hcalBarrelGeometry
    hcalCellPositions = HCalBsegcells
    hcalReadoutName = hcalBarrelReadoutNamePhiEta
    
pileupHcalBarrel = PreparePileup("PreparePileupHcalBarrel",
                                 geometryTool = hcalGeoService,
                                 readoutName = hcalReadoutName,
                                 positionsTool = hcalCellPositions,
                                 layerFieldName = "layer",
                                 towerTool = towers,
                                 noiseTool = readNoisyCellsMap,
                                 histogramName = "hcalBarrelEnergyVsAbsEta",
                                 numLayers = 10,
                                 etaSize = [7,  5,  7,   9,   3,   3,  99],
                                 phiSize = [19, 15, 21, 21,  15,  11, 101])
pileupHcalBarrel.hits.Path=hcalCells

THistSvc().Output = ["rec DATAFILE='" + output_name + "' TYP='ROOT' OPT='RECREATE'"]
THistSvc().PrintAll=True
THistSvc().AutoSave=True
THistSvc().AutoFlush=True
THistSvc().OutputLevel=INFO

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
podioinput.AuditExecute = True

list_of_algorithms = [ podioinput,
                       createemptycells,
                       posHcalBarrel,
                       resegmentHcalBarrel, ]

if resegmentHCal:
    list_of_algorithms += [ createHcalBarrelCells, ]
    
list_of_algorithms += [ pileupEcalBarrel,
                        pileupHcalBarrel ]

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax = -1,
    ExtSvc = [podioevent, geoservice],
#    OutputLevel = DEBUG
 )
