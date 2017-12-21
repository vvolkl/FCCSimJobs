import argparse
simparser = argparse.ArgumentParser()
simparser.add_argument("--bFieldOff", action='store_true', help="Switch OFF magnetic field (default: B field ON)")

simparser.add_argument('-s','--seed', type=int, help='Seed for the random number generator', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)


genTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Type of events to generate
genTypeGroup.add_argument("--singlePart", action='store_true', help="Single particle events")
genTypeGroup.add_argument("--pythia", action='store_true', help="Events generated with Pythia")

from math import pi
singlePartGroup = simparser.add_argument_group('Single particles')
import sys
singlePartGroup.add_argument('-e','--energy', type=int, required='--singlePart' in sys.argv, help='Energy of particle in GeV')
singlePartGroup.add_argument('--etaMin', type=float, default=0., help='Minimal pseudorapidity')
singlePartGroup.add_argument('--etaMax', type=float, default=0., help='Maximal pseudorapidity')
singlePartGroup.add_argument('--phiMin', type=float, default=0, help='Minimal azimuthal angle')
singlePartGroup.add_argument('--phiMax', type=float, default=2*pi, help='Maximal azimuthal angle')
singlePartGroup.add_argument('--particle', type=int, required='--singlePart' in sys.argv, help='Particle type (PDG)')

pythiaGroup = simparser.add_argument_group('Pythia','Common for min bias and LHE')
pythiaGroup.add_argument('-c', '--card', type=str, default='Generation/data/Pythia_minbias_pp_100TeV.cmd', help='Path to Pythia card (default: PythiaCards/default.cmd)')

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
magnetic_field = not simargs.bFieldOff
num_events = simargs.numEvents
seed = simargs.seed
output_name = simargs.outName
print "B field: ", magnetic_field
print "number of events = ", num_events
print "seed: ", seed
print "output name: ", output_name
if simargs.singlePart:
    energy = simargs.energy
    etaMin = simargs.etaMin
    etaMax = simargs.etaMax
    phiMin = simargs.phiMin
    phiMax = simargs.phiMax
    pdg = simargs.particle
    particle_geant_names = {11: 'e-', -11: 'e+', -13: 'mu+', 13: 'mu-', 22: 'gamma', 111: 'pi0', 211: 'pi+', -211: 'pi-', 130: 'kaon0L'}
    print "=================================="
    print "==       SINGLE PARTICLES      ==="
    print "=================================="
    print "particle PDG, name: ", pdg, " ", particle_geant_names[pdg]
    print "energy: ", energy, "GeV"
    if etaMin == etaMax:
        print "eta: ", etaMin
    else:
        print "eta: from ", etaMin, " to ", etaMax
    if phiMin == phiMax:
        print "phi: ", phiMin
    else:
        print "phi: from ", phiMin, " to ", phiMax
elif simargs.pythia:
    card = simargs.card
    print "=================================="
    print "==            PYTHIA           ==="
    print "=================================="
    print "card = ", card
print "=================================="


from Gaudi.Configuration import *
##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################
path_to_detector = '/afs/cern.ch/work/h/helsens/public/FCCsoft/FCCSW-0.8.3/'
detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                  path_to_detector+'/Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalExtendedBarrel_TileCal.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Forward_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Solenoids.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Shielding.xml']

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

# ECAL readouts
ecalBarrelReadoutName = "ECalBarrelEta"
ecalBarrelReadoutNamePhiEta = "ECalBarrelPhiEta"
ecalEndcapReadoutName = "EMECPhiEta"
ecalFwdReadoutName = "EMFwdPhiEta"
# HCAL readouts
hcalBarrelReadoutName = "BarHCal_Readout"
hcalBarrelReadoutNamePhiEta = hcalBarrelReadoutName + "_phieta"
hcalExtBarrelReadoutName = "ExtBarHCal_Readout"
hcalExtBarrelReadoutNamePhiEta = hcalExtBarrelReadoutName + "_phieta"
hcalEndcapReadoutName = "HECPhiEta"
hcalFwdReadoutName = "HFwdPhiEta"
# layers to be merged in endcaps & forward calo
ecalEndcapNumberOfLayersToMerge = [26]*5+[27]
ecalFwdNumberOfLayersToMerge = [7]*5+[8]
hcalEndcapNumberOfLayersToMerge = [13]+[14]*5
hcalFwdNumberOfLayersToMerge = [8]+[9]*5
##############################################################################################################
#######                                        SIMULATION                                        #############
##############################################################################################################
# Setting random seed, will be propagated to Geant
from Configurables import  RndmGenSvc
from GaudiSvc.GaudiSvcConf import HepRndm__Engine_CLHEP__RanluxEngine_
randomEngine = eval('HepRndm__Engine_CLHEP__RanluxEngine_')
randomEngine = randomEngine('RndmGenSvc.Engine')
randomEngine.Seeds = [seed]

from Configurables import SimG4Svc
geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist="SimG4FtfpBert", actions="SimG4FullSimActions")
# range cut
geantservice.g4PostInitCommands += ["/run/setCut 0.1 mm"]

from Configurables import SimG4Alg, SimG4SaveCalHits, SimG4SingleParticleGeneratorTool
saveecaltool = SimG4SaveCalHits("saveECalBarrelHits",readoutNames = [ecalBarrelReadoutName])
saveecaltool.positionedCaloHits.Path = "ECalBarrelPositionedHits"
saveecaltool.caloHits.Path = "ECalBarrelHits"
savehcaltool = SimG4SaveCalHits("saveHCalBarrelHits",readoutNames = [hcalBarrelReadoutName])
savehcaltool.positionedCaloHits.Path = "HCalBarrelPositionedHits"
savehcaltool.caloHits.Path = "HCalBarrelHits"
outputHitsTools = ["SimG4SaveCalHits/saveECalBarrelHits", "SimG4SaveCalHits/saveHCalBarrelHits"]
saveexthcaltool = SimG4SaveCalHits("saveHCalExtBarrelHits",readoutNames = [hcalExtBarrelReadoutName])
saveexthcaltool.positionedCaloHits.Path = "HCalExtBarrelPositionedHits"
saveexthcaltool.caloHits.Path = "HCalExtBarrelHits"
savecalendcaptool = SimG4SaveCalHits("saveECalEndcapHits", readoutNames = [ecalEndcapReadoutName])
savecalendcaptool.positionedCaloHits.Path = "ECalEndcapPositionedHits"
savecalendcaptool.caloHits.Path = "ECalEndcapHits"
savecalfwdtool = SimG4SaveCalHits("saveECalFwdHits", readoutNames = [ecalFwdReadoutName])
savecalfwdtool.positionedCaloHits.Path = "ECalFwdPositionedHits"
savecalfwdtool.caloHits.Path = "ECalFwdHits"
savehcalendcaptool = SimG4SaveCalHits("saveHCalEndcapHits", readoutNames = [hcalEndcapReadoutName])
savehcalendcaptool.positionedCaloHits.Path = "HCalEndcapPositionedHits"
savehcalendcaptool.caloHits.Path = "HCalEndcapHits"
savehcalfwdtool = SimG4SaveCalHits("saveHCalFwdHits", readoutNames = [hcalFwdReadoutName])
savehcalfwdtool.positionedCaloHits.Path = "HCalFwdPositionedHits"
savehcalfwdtool.caloHits.Path = "HCalFwdHits"
outputHitsTools += ["SimG4SaveCalHits/saveECalEndcapHits","SimG4SaveCalHits/saveECalFwdHits",
                    "SimG4SaveCalHits/saveHCalExtBarrelHits", "SimG4SaveCalHits/saveHCalEndcapHits",
                    "SimG4SaveCalHits/saveHCalFwdHits"]

geantsim = SimG4Alg("SimG4Alg", outputs = outputHitsTools)

if simargs.singlePart:
    from Configurables import SimG4SingleParticleGeneratorTool
    pgun=SimG4SingleParticleGeneratorTool("SimG4SingleParticleGeneratorTool", saveEdm=True,
                                          particleName=particle_geant_names[pdg], energyMin=energy * 1000, energyMax=energy * 1000,
                                          etaMin=etaMin, etaMax=etaMax, phiMin = phiMin, phiMax = phiMax)
    geantsim.eventProvider = pgun
else:
    from Configurables import PythiaInterface, GenAlg
    pythia8gentool = PythiaInterface("Pythia8",Filename=card)
    pythia8gen = GenAlg("Pythia8", SignalProvider=pythia8gentool)
    pythia8gen.hepmc.Path = "hepmc"
    from Configurables import HepMCToEDMConverter
    hepmc_converter = HepMCToEDMConverter("Converter")
    hepmc_converter.hepmc.Path="hepmc"
    hepmc_converter.genparticles.Path="allGenParticles"
    hepmc_converter.genvertices.Path="allGenVertices"
    from Configurables import SimG4PrimariesFromEdmTool
    particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
    particle_converter.genParticles.Path = "allGenParticles"
    geantsim.eventProvider = particle_converter

# Magnetic field
from Configurables import SimG4ConstantMagneticFieldTool
if magnetic_field:
    field = SimG4ConstantMagneticFieldTool("bField", FieldOn=True, IntegratorStepper="ClassicalRK4")
else:
    field = SimG4ConstantMagneticFieldTool("bField", FieldOn=False)

##############################################################################################################
#######                                       DIGITISATION                                       #############
##############################################################################################################

# Calibration constants
from Configurables import CalibrateInLayersTool, CalibrateCaloHitsTool
calibEcalBarrel = CalibrateInLayersTool("CalibrateEcalBarrel",
                                        # sampling fraction obtained using SamplingFractionInLayers from DetStudies package
                                        samplingFraction = [0.12125] + [0.14283] + [0.16354] + [0.17662] + [0.18867] + [0.19890] + [0.20637] + [0.20802],
                                        readoutName = ecalBarrelReadoutName,
                                        layerFieldName = "layer")
calibHcells = CalibrateCaloHitsTool("CalibrateHCal", invSamplingFraction="41.66")
calibEcalEndcap = CalibrateCaloHitsTool("CalibrateECalEndcap", invSamplingFraction="13.89")
calibEcalFwd = CalibrateCaloHitsTool("CalibrateECalFwd", invSamplingFraction="303.03")
calibHcalEndcap = CalibrateCaloHitsTool("CalibrateHCalEndcap", invSamplingFraction="33.62")
calibHcalFwd = CalibrateCaloHitsTool("CalibrateHCalFwd", invSamplingFraction="1207.7")

# Create cells
from Configurables import CreateCaloCells
# -> ECal barrel
# 1. step - merge hits into cells with default Eta segmentation
createEcalBarrelCellsStep1 = CreateCaloCells("EcalBarrelCellsStep1",
                                             doCellCalibration=True,
                                             calibTool=calibEcalBarrel,
                                             addCellNoise=False, filterCellNoise=False)
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
resegmentEcalBarrel = RedoSegmentation("ReSegmentationEcalBarrel",
                                       oldReadoutName = 'ECalBarrelEta',
                                       oldSegmentationIds = ['module'],
                                       newReadoutName = 'ECalBarrelPhiEta',
                                       inhits = "ECalBarrelPositions",
                                       outhits = "ECalBarrelCellsStep2")
# 3. step - merge cells in the same phi bin
createEcalBarrelCells = CreateCaloCells("CreateECalBarrelCells",
                                        doCellCalibration=False, # already calibrated in step 1
                                        addCellNoise=False, filterCellNoise=False,
                                        hits="ECalBarrelCellsStep2",
                                        cells="ECalBarrelCells")

# -> Ecal endcaps and forward
createEcalEndcapCells = CreateCaloCells("EcalEndcapCells",
                                        doCellCalibration=True,
                                        calibTool=calibEcalEndcap,
                                        addCellNoise=False, filterCellNoise=False)
createEcalEndcapCells.hits.Path="ECalEndcapHits"
createEcalEndcapCells.cells.Path="ECalEndcapCells"
createEcalFwdCells = CreateCaloCells("EcalFwdCells",
                                     doCellCalibration=True,
                                     calibTool=calibEcalFwd,
                                     addCellNoise=False, filterCellNoise=False)
createEcalFwdCells.hits.Path="ECalFwdHits"
createEcalFwdCells.cells.Path="ECalFwdCells"

# -> Hcal barrel
createHcalCells = CreateCaloCells("CreateHCalBarrelCells",
                                  doCellCalibration=True,
                                  calibTool=calibHcells,
                                  addCellNoise = False, filterCellNoise = False,
                                  hits="HCalBarrelHits",
                                  cells="HCalBarrelCells")

# -> Hcal extended barrel
createExtHcalCells = CreateCaloCells("CreateExtHcalCaloCells",
                                     doCellCalibration=True,
                                     calibTool=calibHcells,
                                     addCellNoise = False, filterCellNoise = False,
                                     hits="HCalExtBarrelHits",
                                     cells="HCalExtBarrelCells")

# -> Hcal endcaps and forward
createHcalEndcapCells = CreateCaloCells("CreateHcalEndcapCaloCells",
                                        doCellCalibration=True,
                                        calibTool=calibHcalEndcap,
                                        addCellNoise=False, filterCellNoise=False)
createHcalEndcapCells.hits.Path="HCalEndcapHits"
createHcalEndcapCells.cells.Path="HCalEndcapCells"
createHcalFwdCells = CreateCaloCells("CreateHcalFwdCaloCells",
                                     doCellCalibration=True,
                                     calibTool=calibHcalFwd,
                                     addCellNoise=False, filterCellNoise=False)
createHcalFwdCells.hits.Path="HCalFwdHits"
createHcalFwdCells.cells.Path="HCalFwdCells"

# PODIO algorithm
from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput
podioevent = FCCDataSvc("EventDataSvc")
out = PodioOutput("out")
out.outputCommands = ["drop *",
                      "keep ECalBarrelCells",
                      "keep ECalEndcapCells",
                      "keep ECalFwdCells",
                      "keep HCalBarrelCells",
                      "keep HCalExtBarrelCells",
                      "keep HCalEndcapCells",
                      "keep HCalFwdCells"]
out.filename = output_name

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
geantsim.AuditExecute = True
createEcalBarrelCellsStep1.AuditExecute = True
positionsEcalBarrel.AuditExecute = True
resegmentEcalBarrel.AuditExecute = True
createEcalBarrelCells.AuditExecute = True
createHcalCells.AuditExecute = True
createEcalEndcapCells.AuditExecute = True
createHcalEndcapCells.AuditExecute = True
createHcalFwdCells.AuditExecute = True
out.AuditExecute = True

list_of_algorithms = [geantsim,
                      createEcalBarrelCellsStep1,
                      positionsEcalBarrel,
                      resegmentEcalBarrel,
                      createEcalBarrelCells,
                      createHcalCells,
                      createEcalEndcapCells,
                      createEcalFwdCells,
                      createExtHcalCells,
                      createHcalEndcapCells,
                      createHcalFwdCells,
                      out]

if simargs.pythia:
    list_of_algorithms = [pythia8gen, hepmc_converter] + list_of_algorithms

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [podioevent, geoservice, geantservice],
)
