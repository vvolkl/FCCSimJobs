import argparse
simparser = argparse.ArgumentParser()
simparser.add_argument('--inName', type=str, nargs = "+", help='Name of the input file', required=True)
simparser.add_argument('--inSignalName', type=str, help='Name of the input file with signal')
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--pileup', type=int, help='Pileup', default = 1000)
simparser.add_argument('--rebase', action='store_true', help='Rebase the merged PU to baseline 0, with averaged mean values.', default=False)
simparser.add_argument('--prefixCollections', type=str, help='Prefix added to the collection names', default="")
simparser.add_argument('--detectorPath', type=str, help='Path to detectors', default = "/afs/cern.ch/work/c/cneubuse/public/TopoClusters/FCCSW/")
simparser.add_argument("--resegmentHCal", action='store_true', help="Merge HCal cells in DeltaEta=0.025 bins", default = False)
simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
rebase = simargs.rebase
input_name = simargs.inName
pileup = simargs.pileup
prefix = simargs.prefixCollections
noSignal = True
path_to_detector = simargs.detectorPath
resegmentHCal = simargs.resegmentHCal
if simargs.inSignalName:
    signalFilename = simargs.inSignalName
    print "input signal name: ", signalFilename
    noSignal = False
output_name = simargs.outName
print "input pileup name: ", input_name
print "output name: ", output_name
print "rebase mean energy/cell to 0: ", rebase
print "no signal: ", noSignal
print "=================================="

from Gaudi.Configuration import *

# list of names of files with pileup event data -- to be overlaid
pileupFilenames = input_name
# the file containing the signal events
if simargs.inSignalName:
    # the collections to be read from the signal event
    signalCollections = ["GenParticles", "GenVertices",
                         "ECalBarrelCells", "ECalEndcapCells", "ECalFwdCells",
                         "HCalBarrelCells", "HCalExtBarrelCells", "HCalEndcapCells", "HCalFwdCells"]
    # Data service
    from Configurables import ApplicationMgr, FCCDataSvc, PodioInput, PodioOutput
    podioevent = FCCDataSvc("EventDataSvc", input=signalFilename)
    
    # use PodioInput for Signal
    podioinput = PodioInput("PodioReader", collections=signalCollections)
    
    list_of_algorithms = [podioinput]
    pileup = 1

else:
    noSignal = True
    list_of_algorithms = []
    from Configurables import FCCDataSvc
    podioevent = FCCDataSvc("EventDataSvc")


detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml']

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

import random
seed=int(filter(str.isdigit, output_name))
print 'seed : ', seed
random.seed(seed)
random.shuffle(pileupFilenames)

# edm data from generation: particles and vertices
from Configurables import PileupParticlesMergeTool
particlemergetool = PileupParticlesMergeTool("ParticlesMerge")
# branchnames for the pileup
particlemergetool.genParticlesBranch = "GenParticles"
particlemergetool.genVerticesBranch = "GenVertices"
# branchnames for the signal
particlemergetool.signalGenParticles.Path = "GenParticles"
particlemergetool.signalGenVertices.Path = "GenVertices"
# branchnames for the output
particlemergetool.mergedGenParticles.Path = "pileupGenParticles"
particlemergetool.mergedGenVertices.Path = "pileupGenVertices"

# edm data from simulation: hits and positioned hits
from Configurables import PileupCaloHitMergeTool
ecalbarrelmergetool = PileupCaloHitMergeTool("ECalBarrelHitMerge")
ecalbarrelmergetool.pileupHitsBranch = prefix+"ECalBarrelCells"
ecalbarrelmergetool.signalHits = "ECalBarrelCells"
ecalbarrelmergetool.mergedHits = "pileupECalBarrelCells"

# edm data from simulation: hits and positioned hits
ecalendcapmergetool = PileupCaloHitMergeTool("ECalEndcapHitMerge")
ecalendcapmergetool.pileupHitsBranch = prefix+"ECalEndcapCells"
ecalendcapmergetool.signalHits = "ECalEndcapCells"
ecalendcapmergetool.mergedHits = "pileupECalEndcapCells"

# edm data from simulation: hits and positioned hits
ecalfwdmergetool = PileupCaloHitMergeTool("ECalFwdHitMerge")
# branchnames for the pileup
ecalfwdmergetool.pileupHitsBranch = prefix+"ECalFwdCells"
ecalfwdmergetool.signalHits = "ECalFwdCells"
ecalfwdmergetool.mergedHits = "pileupECalFwdCells"

# edm data from simulation: hits and positioned hits
hcalbarrelmergetool = PileupCaloHitMergeTool("HCalBarrelHitMerge")
hcalbarrelmergetool.pileupHitsBranch = prefix+"HCalBarrelCells"
hcalbarrelmergetool.signalHits = "HCalBarrelCells"
hcalbarrelmergetool.mergedHits = "pileupHCalBarrelCells"

# edm data from simulation: hits and positioned hits
hcalextbarrelmergetool = PileupCaloHitMergeTool("HCalExtBarrelHitMerge")
hcalextbarrelmergetool.pileupHitsBranch = prefix+"HCalExtBarrelCells"
hcalextbarrelmergetool.signalHits = "HCalExtBarrelCells"
hcalextbarrelmergetool.mergedHits = "pileupHCalExtBarrelCells"

# edm data from simulation: hits and positioned hits
hcalfwdmergetool = PileupCaloHitMergeTool("HCalFwdHitMerge")
hcalfwdmergetool.pileupHitsBranch = prefix+"HCalFwdCells"
hcalfwdmergetool.signalHits = "HCalFwdCells"
hcalfwdmergetool.mergedHits = "pileupHCalFwdCells"

# edm data from simulation: hits and positioned hits
hcalfwdmergetool = PileupCaloHitMergeTool("HCalEndcapHitMerge")
hcalfwdmergetool.pileupHitsBranch = prefix+"HCalEndcapCells"
hcalfwdmergetool.signalHits = "HCalEndcapCells"
hcalfwdmergetool.mergedHits = "pileupHCalEndcapCells"

# use the pileuptool to specify the number of pileup
from Configurables import ConstPileUp
pileuptool = ConstPileUp("MyPileupTool", numPileUpEvents=pileup)

# algorithm for the overlay
from Configurables import PileupOverlayAlg
overlay = PileupOverlayAlg()
overlay.pileupFilenames = pileupFilenames
overlay.doShuffleInputFiles = True
overlay.randomizePileup = True
overlay.mergeTools = [
    "PileupCaloHitMergeTool/ECalBarrelHitMerge",
    "PileupCaloHitMergeTool/HCalBarrelHitMerge",
    ]

if not rebase:
    overlay.mergeTools += [
        "PileupCaloHitMergeTool/ECalEndcapHitMerge",
        "PileupCaloHitMergeTool/ECalFwdHitMerge",
        "PileupCaloHitMergeTool/HCalExtBarrelHitMerge",
        "PileupCaloHitMergeTool/HCalEndcapHitMerge",
        "PileupCaloHitMergeTool/HCalFwdHitMerge"
        ]
    
overlay.PileUpTool = pileuptool
overlay.noSignal = noSignal

ecalBarrelOutput1 = "mergedECalBarrelCells"
hcalBarrelOutput1 = "mergedHCalBarrelCells"
hcalBarrelOutput2 = ""
if rebase:
    # name of output of pileup merge
    ecalBarrelOutput1 = "mergedECalBarrelCellsStep1"
    hcalBarrelOutput1 = "mergedHCalBarrelCellsStep1"
    # input for rebase
    hcalBarrelOutput2 = hcalBarrelOutput1
    if resegmentHCal:
        hcalBarrelOutput2 = "newHCalBarrelCells"

##############################################################################################################
#######                                       DIGITISATION                                       #############
##############################################################################################################

from Configurables import CreateCaloCells
createEcalBarrelCells = CreateCaloCells("CreateEcalBarrelCells",
                                        doCellCalibration=False, recalibrateBaseline =False,
                                        addCellNoise=False, filterCellNoise=False)
createEcalBarrelCells.hits.Path="pileupECalBarrelCells"
createEcalBarrelCells.cells.Path=ecalBarrelOutput1
createEcalEndcapCells = CreateCaloCells("CreateEcalEndcapCells",
                                        doCellCalibration=False, recalibrateBaseline =False,
                                        addCellNoise=False, filterCellNoise=False)
createEcalEndcapCells.hits.Path="pileupECalEndcapCells"
createEcalEndcapCells.cells.Path="mergedECalEndcapCells"
createEcalFwdCells = CreateCaloCells("CreateEcalFwdCells",
                                     doCellCalibration=False, recalibrateBaseline =False,
                                     addCellNoise=False, filterCellNoise=False)
createEcalFwdCells.hits.Path="pileupECalFwdCells"
createEcalFwdCells.cells.Path="mergedECalFwdCells"
createHcalBarrelCells = CreateCaloCells("CreateHcalBarrelCells",
                                        doCellCalibration=False, recalibrateBaseline =False,
                                        addCellNoise=False, filterCellNoise=False)
createHcalBarrelCells.hits.Path="pileupHCalBarrelCells"
createHcalBarrelCells.cells.Path=hcalBarrelOutput1
createHcalExtBarrelCells = CreateCaloCells("CreateHcalExtBarrelCells",
                                           doCellCalibration=False, recalibrateBaseline =False,
                                           addCellNoise=False, filterCellNoise=False)
createHcalExtBarrelCells.hits.Path="pileupHCalExtBarrelCells"
createHcalExtBarrelCells.cells.Path="mergedHCalExtBarrelCells"
createHcalEndcapCells = CreateCaloCells("CreateHcalEndcapCells",
                                        doCellCalibration=False, recalibrateBaseline =False,
                                        addCellNoise=False, filterCellNoise=False)
createHcalEndcapCells.hits.Path="pileupHCalEndcapCells"
createHcalEndcapCells.cells.Path="mergedHCalEndcapCells"
createHcalFwdCells = CreateCaloCells("CreateHcalFwdCells",
                                     doCellCalibration=False, recalibrateBaseline =False,
                                     addCellNoise=False, filterCellNoise=False)
createHcalFwdCells.hits.Path="pileupHCalFwdCells"
createHcalFwdCells.cells.Path="mergedHCalFwdCells"

########
# RESEGMENT HCAL CELLS
########
from Configurables import CreateVolumeCaloPositions,RedoSegmentation,CreateCaloCells
# Create cells in HCal
# 2. step - rewrite the cellId using the Phi-Eta segmentation
# 3. step - merge new cells corresponding to eta-phi segmentation
# Hcal barrel cell positions
posHcalBarrel = CreateVolumeCaloPositions("posBarrelHcal", OutputLevel = INFO)
posHcalBarrel.hits.Path = hcalBarrelOutput1
posHcalBarrel.positionedHits.Path = "HCalBarrelPositions"

# Use Phi-Eta segmentation in Hcal barrel
resegmentHcalBarrel = RedoSegmentation("ReSegmentationHcal",
                                       # old bitfield (readout)
                                       oldReadoutName = "HCalBarrelReadout",
                                       # specify which fields are going to be altered (deleted/rewritten)
                                       oldSegmentationIds = ["module","row"],
                                       # new bitfield (readout), with new segmentation
                                       newReadoutName = "BarHCal_Readout_phieta",
                                       inhits = "HCalBarrelPositions",
                                       outhits = "HCalBarrelCellsStep2")

createSegHcalBarrelCells = CreateCaloCells("CreateSegHCalBarrelCells",
                                           doCellCalibration=False, recalibrateBaseline =False,
                                           addCellNoise=False, filterCellNoise=False,
                                           hits="HCalBarrelCellsStep2",
                                           cells="newHCalBarrelCells")

##############################################################################################################
#######                                       REBASE PU TO 0                              #############
##############################################################################################################
# Need to resegment HCal cells
# pileup noise levels always in DeltaEta=0.025 cells

#Configure tools for calo cell positions
inputPileupNoisePerCell = "/afs/cern.ch/work/c/cneubuse/public/FCChh/inBfield/cellNoise_map_electronicsNoiseLevel_forPU"+str(simargs.pileup)+".root"
if resegmentHCal:
    inputPileupNoisePerCell = "/afs/cern.ch/work/c/cneubuse/public/FCChh/inBfield/resegmentedHCal/cellNoise_map_electronicsNoiseLevel_forPU"+str(simargs.pileup)+".root"

from Configurables import TopoCaloNoisyCells
readNoisyCellsMap = TopoCaloNoisyCells("ReadNoisyCellsMap",
                                       fileName = inputPileupNoisePerCell)

rebaseEcalBarrelCells = CreateCaloCells("RebaseECalBarrelCells",
                                        doCellCalibration=False,
                                        addCellNoise=False, filterCellNoise=False,
                                        recalibrateBaseline =True,
                                        readCellNoiseTool = readNoisyCellsMap,
                                        hits=ecalBarrelOutput1,
                                        cells="mergedECalBarrelCells")

rebaseHcalBarrelCells = CreateCaloCells("RebaseHCalBarrelCells",
                                        doCellCalibration=False,
                                        addCellNoise=False, filterCellNoise=False,
                                        recalibrateBaseline =True,
                                        readCellNoiseTool = readNoisyCellsMap,
                                        hits=hcalBarrelOutput2,
                                        cells="mergedHCalBarrelCells")
# PODIO algorithm
from Configurables import PodioOutput
out = PodioOutput("out")
out.outputCommands = ["drop *", "keep GenVertices", "keep GenParticles", "keep mergedECalBarrelCells", "keep mergedECalEndcapCells", "keep mergedECalFwdCells", "keep mergedHCalBarrelCells", "keep mergedHCalExtBarrelCells", "keep mergedHCalEndcapCells", "keep mergedHCalFwdCells"]
out.filename = output_name

list_of_algorithms += [overlay,
                       createEcalBarrelCells,
                       createHcalBarrelCells,
                       ]
if not rebase:
    list_of_algorithms += [
        createEcalEndcapCells,
        createEcalFwdCells,
        createHcalBarrelCells,
        createHcalExtBarrelCells,
        createHcalEndcapCells,
        createHcalFwdCells,
        ]
    
if rebase:
    if resegmentHCal:
        list_of_algorithms += [
            posHcalBarrel,
            resegmentHcalBarrel, 
            createSegHcalBarrelCells, ]
    list_of_algorithms += [
        rebaseEcalBarrelCells,
        rebaseHcalBarrelCells, ]
    
list_of_algorithms += [out]

# ApplicationMgr
from Configurables import ApplicationMgr
ApplicationMgr( TopAlg=list_of_algorithms,
                EvtSel='NONE',
                EvtMax=num_events,
                ExtSvc=[geoservice,podioevent],
#                OutputLevel = DEBUG
                )
