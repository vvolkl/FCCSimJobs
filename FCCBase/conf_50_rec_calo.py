

ecalBarrelReadoutName = "ECalBarrelEta" # todo import from det package

# Calibration constants
from Configurables import CalibrateInLayersTool
calibEcalBarrel = CalibrateInLayersTool("CalibrateEcalBarrel")

# sampling fraction obtained using SamplingFractionInLayers from DetStudies package
calibEcalBarrel = samplingFraction = [ 
                                        0.299041341789,
                                        0.1306220735,
                                        0.163243999965,
                                        0.186360269398,
                                        0.203778124831,
                                        0.216211280314,
                                        0.227140796653,
                                        0.243315422934,
                                      ]
calibEcalBarrel.readoutName = ecalBarrelReadoutName
calibEcalBarrel.layerFieldName = "layer"

from Configurables import CalibrateCaloHitsTool
calibHcells = CalibrateCaloHitsTool("CalibrateHCal")
calibHcells.invSamplingFraction = "41.66"

calibEcalEndcap = CalibrateCaloHitsTool("CalibrateECalEndcap")
calibEcalEndcap.invSamplingFraction="13.89"

calibEcalFwd = CalibrateCaloHitsTool("CalibrateECalFwd")
calibEcalFwd.invSamplingFraction="303.03"

calibHcalEndcap = CalibrateCaloHitsTool("CalibrateHCalEndcap")
calibHcalEndcap.invSamplingFraction="33.62"

calibHcalFwd = CalibrateCaloHitsTool("CalibrateHCalFwd")
calibHcalFwd.invSamplingFraction="1207.7")


# Create cells
from Configurables import CreateCaloCells
# -> ECal barrel
# 1. step - merge hits into cells with default Eta segmentation
createEcalBarrelCellsStep1 = CreateCaloCells("EcalBarrelCellsStep1")
createEcalBarrelCellsStep1.doCellCalibration = True
createEcalBarrelCellsStep1.calibTool = calibEcalBarrel
createEcalBarrelCellsStep1.addCellNoise = False
createEcalBarrelCellsStep1.filterCellNoise = False
createEcalBarrelCellsStep1.hits.Path="ECalBarrelHits"
createEcalBarrelCellsStep1.cells.Path="ECalBarrelCellsStep1"

# 2. step - rewrite the cellId using the Phi-Eta segmentation (remove 'module')
# 2.1. retrieve phi positions from centres of cells
from Configurables import CreateVolumeCaloPositions
positionsEcalBarrel = CreateVolumeCaloPositions("positionsEcalBarrel")
positionsEcalBarrel.hits.Path = "ECalBarrelCellsStep1"
positionsEcalBarrel.positionedHits.Path = "ECalBarrelPositions"

# 2.2. assign cells into phi bins
from Configurables import RedoSegmentation
resegmentEcalBarrel = RedoSegmentation("ReSegmentationEcalBarrel")
resegmentEcalBarrel.oldReadoutName = 'ECalBarrelEta'
resegmentEcalBarrel.oldSegmentationIds = ['module']
resegmentEcalBarrel.newReadoutName = 'ECalBarrelPhiEta'
resegmentEcalBarrel.inhits = "ECalBarrelPositions"
resegmentEcalBarrel.outhits = "ECalBarrelCellsStep2"

# 3. step - merge cells in the same phi bin
createEcalBarrelCells = CreateCaloCells("CreateECalBarrelCells")
createEcalBarrelCells.doCellCalibration = False # already calibrated in step 1
createEcalBarrelCells.addCellNoise = False
createEcalBarrelCells.filterCellNoise = False
createEcalBarrelCells.hits = "ECalBarrelCellsStep2"
createEcalBarrelCells.cells = "ECalBarrelCells"

