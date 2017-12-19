import argparse
simparser = argparse.ArgumentParser()
geoTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Which calorimeters to include (always include beampipe and tracker)
geoTypeGroup.add_argument("--geoFull", action='store_true', help="Full geometry assembly (barrel, endcaps, forward) (default)")
geoTypeGroup.add_argument("--geoBarrel", action='store_true', help="Only calo barrel")
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
if simargs.geoFull:
    print "full geometry assembly"
elif simargs.geoBarrel:
    print "only barrel"
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
    particle_human_names = {11: 'electron', -11: 'positron', -13: 'mup', 13: 'mum', 22: 'photon', 111: 'pi0', 211: 'pip', -211: 'pim'}
    particle_geant_names = {11: 'e-', -11: 'e+', -13: 'mu+', 13: 'mu-', 22: 'gamma', 111: 'pi0', 211: 'pi+', -211: 'pi-' }
    print "=================================="
    print "==       SINGLE PARTICLES      ==="
    print "=================================="
    print "particle PDG, name: ", pdg, " ", particle_human_names[pdg], " ", particle_geant_names[pdg]
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
detectors_to_use=['file:Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  'file:Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                  'file:Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                  'file:Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml']
# TODO add: beampipe and shielding
if simargs.geoFull:
    detectors_to_use += ['file:Detector/DetFCChhHCalTile/compact/FCChh_HCalExtendedBarrel_TileCal.xml',
                         'file:Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml',
                         'file:Detector/DetFCChhCalDiscs/compact/Forward_coneCryo.xml' ]
print detectors_to_use

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

##############################################################################################################
#######                                        SIMULATION                                        #############
##############################################################################################################
#Setting random seed, will be propagated to Geant
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
saveecaltool = SimG4SaveCalHits("saveECalBarrelHits",readoutNames = ["ECalBarrelEta"])
saveecaltool.positionedCaloHits.Path = "ECalBarrelPositionedHits"
saveecaltool.caloHits.Path = "ECalBarrelHits"
savehcaltool = SimG4SaveCalHits("saveHCalHits",readoutNames = ["BarHCal_Readout"])
savehcaltool.positionedCaloHits.Path = "HCalPositionedHits"
savehcaltool.caloHits.Path = "HCalHits"
outputHitsTools = ["SimG4SaveCalHits/saveECalBarrelHits", "SimG4SaveCalHits/saveHCalHits", ]
if simargs.geoFull:
    saveexthcaltool = SimG4SaveCalHits("saveExtHCalHits",readoutNames = ["ExtBarHCal_Readout"])
    saveexthcaltool.positionedCaloHits.Path = "ExtHCalPositionedHits"
    saveexthcaltool.caloHits.Path = "ExtHCalHits"
    savecalendcaptool = SimG4SaveCalHits("saveECalEndcapHits", readoutNames = ["EMECPhiEta"])
    savecalendcaptool.positionedCaloHits.Path = "ECalEndcapPositionedHits"
    savecalendcaptool.caloHits.Path = "ECalEndcapHits"
    savecalfwdtool = SimG4SaveCalHits("saveECalFwdHits", readoutNames = ["EMFwdPhiEta"])
    savecalfwdtool.positionedCaloHits.Path = "ECalFwdPositionedHits"
    savecalfwdtool.caloHits.Path = "ECalFwdHits"
    savehcalendcaptool = SimG4SaveCalHits("saveHCalEndcapHits", readoutNames = ["HECPhiEta"])
    savehcalendcaptool.positionedCaloHits.Path = "HCalEndcapPositionedHits"
    savehcalendcaptool.caloHits.Path = "HCalEndcapHits"
    savehcalfwdtool = SimG4SaveCalHits("saveHCalFwdHits", readoutNames = ["HFwdPhiEta"])
    savehcalfwdtool.positionedCaloHits.Path = "HCalFwdPositionedHits"
    savehcalfwdtool.caloHits.Path = "HCalFwdHits"
    outputHitsTools += ["SimG4SaveCalHits/saveECalEndcapHits","SimG4SaveCalHits/saveECalFwdHits",
                       "SimG4SaveCalHits/saveExtHCalHits", "SimG4SaveCalHits/saveHCalEndcapHits",
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

# ECAL readouts
ecalBarrelReadoutName = "ECalBarrelEta"
ecalBarrelReadoutNamePhiEta = "ECalBarrelPhiEta"
ecalEndcapReadoutName = "EMECPhiEta"
ecalFwdReadoutName = "EMFwdPhiEta"
# HCAL readouts
hcalReadoutName = "BarHCal_Readout"
newHcalReadoutName = hcalReadoutName + "_phieta"
extHcalReadoutName = "ExtBarHCal_Readout"
newExtHcalReadoutName = extHcalReadoutName + "_phieta"
hcalEndcapReadoutName = "HECPhiEta"
hcalFwdReadoutName = "HFwdPhiEta"
# layers to be merged in endcaps & forward calo
ecalEndcapNumberOfLayersToMerge = [26]*5+[27]
ecalFwdNumberOfLayersToMerge = [7]*5+[8]
hcalEndcapNumberOfLayersToMerge = [13]+[14]*5
hcalFwdNumberOfLayersToMerge = [8]+[9]*5
identifierName = "layer"
volumeName = "layer"

# Calibration constants
from Configurables import CalibrateInLayersTool, CalibrateCaloHitsTool
calibEcalBarrel = CalibrateInLayersTool("CalibrateEcalBarrel",
                                   # sampling fraction obtained using SamplingFractionInLayers from DetStudies package
                                   samplingFraction = [0.12125] + [0.14283] + [0.16354] + [0.17662] + [0.18867] + [0.19890] + [0.20637] + [0.20802],
                                   readoutName = "ECalBarrelEta",
                                   layerFieldName = "layer")
calibHcells = CalibrateCaloHitsTool("CalibrateHCal", invSamplingFraction="34.5")
if simargs.geoFull:
    calibEcalEndcap = CalibrateCaloHitsTool("CalibrateECalEndcap", invSamplingFraction="13.89")
    calibEcalFwd = CalibrateCaloHitsTool("CalibrateECalFwd", invSamplingFraction="303.03")
    # TODO take new values with Pb spacers!!!
    calibHcalEndcap = CalibrateCaloHitsTool("CalibrateHCalEndcap", invSamplingFraction="34.72")
    calibHcalFwd = CalibrateCaloHitsTool("CalibrateHCalFwd", invSamplingFraction="30303.")

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


if simargs.geoFull:
    # -> Ecal endcaps and forward
    from Configurables import MergeLayers
    mergelayersEcalEndcap = MergeLayers("MergeLayersEcalEndcap",
                                        # take the bitfield description from the geometry service
                                        readout = ecalEndcapReadoutName,
                                        # cells in which field should be merged
                                        identifier = identifierName,
                                        volumeName = volumeName,
                                        # how many cells to merge
                                        merge = ecalEndcapNumberOfLayersToMerge)
    mergelayersEcalEndcap.inhits.Path = "ECalEndcapHits"
    mergelayersEcalEndcap.outhits.Path = "mergedECalEndcapHits"
    createEcalEndcapCells = CreateCaloCells("EcalEndcapCells",
                                            doCellCalibration=True,
                                            calibTool=calibEcalEndcap,
                                            addCellNoise=False, filterCellNoise=False)
    createEcalEndcapCells.hits.Path="mergedECalEndcapHits"
    createEcalEndcapCells.cells.Path="ECalEndcapCells"
    mergelayersEcalFwd = MergeLayers("MergeLayersEcalFwd",
                                     readout = ecalFwdReadoutName,
                                     identifier = identifierName,
                                     volumeName = volumeName,
                                     merge = ecalFwdNumberOfLayersToMerge)
    mergelayersEcalFwd.inhits.Path = "ECalFwdHits"
    mergelayersEcalFwd.outhits.Path = "mergedECalFwdHits"
    createEcalFwdCells = CreateCaloCells("EcalFwdCells",
                                         doCellCalibration=True,
                                         calibTool=calibEcalFwd,
                                         addCellNoise=False, filterCellNoise=False)
    createEcalFwdCells.hits.Path="mergedECalFwdHits"
    createEcalFwdCells.cells.Path="ECalFwdCells"

# -> Hcal barrel
# 1. step - merge hits into cells with the default readout
createHcalCells = CreateCaloCells("CreateHCaloCells",
                               doCellCalibration=True,
                               calibTool=calibHcells,
                               addCellNoise = False, filterCellNoise = False,
                               hits="HCalHits",
                               cells="HCalCells")
# 2. step - rewrite the cellId using the Phi-Eta segmentation
# 2.1. get positions from centres of volumes/cells
positionsHcal = CreateVolumeCaloPositions("positionsHcal")
positionsHcal.hits.Path = "HCalCells"
positionsHcal.positionedHits.Path = "HCalPositions"
# 2.2. assign cells into phi bins
from Configurables import RedoSegmentation
resegmentHcal = RedoSegmentation("ReSegmentationHcal",
                             oldReadoutName = hcalReadoutName,
                             oldSegmentationIds = ["eta","phi"],
                             newReadoutName = newHcalReadoutName,
                             debugPrint = 10,
                             inhits = "HCalPositions",
                             outhits = "newHCalCells")

if simargs.geoFull:
    # -> Hcal extended barrel
    # 1. step - merge hits into cells with the default readout
    createExtHcalCells = CreateCaloCells("CreateExtHcalCaloCells",
                                         doCellCalibration=True,
                                         calibTool=calibHcells,
                                         addCellNoise = False, filterCellNoise = False,
                                         hits="ExtHCalHits",
                                         cells="ExtHCalCells")
    # 2. step - rewrite the cellId using the Phi-Eta segmentation
    # 2.1. get positions from centres of volumes/cells
    positionsExtHcal = CreateVolumeCaloPositions("positionsExtHcal")
    positionsExtHcal.hits.Path = "ExtHCalCells"
    positionsExtHcal.positionedHits.Path = "ExtHCalPositions"
    # 2.2. assign cells into phi bins
    resegmentExtHcal = RedoSegmentation("ReSegmentationExtHcal",
                                    oldReadoutName = extHcalReadoutName,
                                    oldSegmentationIds = ["eta","phi"],
                                    newReadoutName = newExtHcalReadoutName,
                                    debugPrint = 10,
                                        inhits = "ExtHCalPositions",
                                        outhits = "newExtHCalCells")

    # -> Hcal endcaps and forward
    mergelayersHcalEndcap = MergeLayers("MergeLayersHcalEndcap",
                                        readout = hcalEndcapReadoutName,
                                        identifier = identifierName,
                                        volumeName = volumeName,
                                        merge = hcalEndcapNumberOfLayersToMerge)
    mergelayersHcalEndcap.inhits.Path = "HCalEndcapHits"
    mergelayersHcalEndcap.outhits.Path = "mergedHCalEndcapHits"
    createHcalEndcapCells = CreateCaloCells("CreateHcalEndcapCaloCells",
                                            doCellCalibration=True,
                                            calibTool=calibHcalEndcap,
                                            addCellNoise=False, filterCellNoise=False)
    createHcalEndcapCells.hits.Path="mergedHCalEndcapHits"
    createHcalEndcapCells.cells.Path="HCalEndcapCells"
    mergelayersHcalFwd = MergeLayers("MergeLayersHcalFwd",
                                     readout = hcalFwdReadoutName,
                                     identifier = identifierName,
                                     volumeName = volumeName,
                                     merge = hcalFwdNumberOfLayersToMerge)
    mergelayersHcalFwd.inhits.Path = "HCalFwdHits"
    mergelayersHcalFwd.outhits.Path = "mergedHCalFwdHits"
    createHcalFwdCells = CreateCaloCells("CreateHcalFwdCaloCells",
                                         doCellCalibration=True,
                                         calibTool=calibHcalFwd,
                                         addCellNoise=False, filterCellNoise=False)
    createHcalFwdCells.hits.Path="mergedHCalFwdHits"
    createHcalFwdCells.cells.Path="HCalFwdCells"

# PODIO algorithm
from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput
podioevent = FCCDataSvc("EventDataSvc")
out = PodioOutput("out")
out.outputCommands = ["drop *", "keep ECalBarrelCells", "keep ECalEndcapCells", "keep ECalFwdCells", "keep newHCalCells", "keep newExtHCalCells", "keep HCalEndcapCells", "keep HCalFwdCells"]
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
positionsHcal.AuditExecute = True
resegmentHcal.AuditExecute = True
if simargs.geoFull:
    createEcalEndcapCells.AuditExecute = True
    createEcalFwdCells.AuditExecute = True
    createExtHcalCells.AuditExecute = True
    positionsExtHcal.AuditExecute = True
    resegmentExtHcal.AuditExecute = True
    createHcalEndcapCells.AuditExecute = True
    createHcalFwdCells.AuditExecute = True
out.AuditExecute = True

list_of_algorithms = [geantsim,
              createEcalBarrelCellsStep1,
              positionsEcalBarrel,
              resegmentEcalBarrel,
              createEcalBarrelCells,
              createHcalCells,
              positionsHcal,
              resegmentHcal]

if simargs.pythia:
    list_of_algorithms = [pythia8gen, hepmc_converter] + list_of_algorithms
if simargs.geoFull:
    list_of_algorithms += [mergelayersEcalEndcap,
                           createEcalEndcapCells,
                           mergelayersEcalFwd,
                           createEcalFwdCells,
                           createExtHcalCells,
                           positionsExtHcal,
                           resegmentExtHcal,
                           mergelayersHcalEndcap,
                           createHcalEndcapCells,
                           mergelayersHcalFwd,
                           createHcalFwdCells]
list_of_algorithms += out

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [podioevent, geoservice, geantservice],
)
