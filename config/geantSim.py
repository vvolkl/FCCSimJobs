import argparse
simparser = argparse.ArgumentParser()
geoTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Which calorimeters to include (always include beampipe and tracker)
geoTypeGroup.add_argument("--geoFull", action='store_true', help="Full geometry assembly (barrel, endcaps, forward) (default)")
geoTypeGroup.add_argument("--geoBarrel", action='store_true', help="Only calo barrel")
simparser.add_argument("--bFieldOff", action='store_true', help="Switch OFF magnetic field (default: B field ON)")

simparser.add_argument('-s','--seed', type=int, help='Seed for the random number generator', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('-o','--output', type=str, help='Name of the output file', required=True)


genTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Type of events to generate
genTypeGroup.add_argument("--singlePart", action='store_true', help="Single particle events")
genTypeGroup.add_argument("--minBias", action='store_true', help="Minimum bias events generated with Pythia")
genTypeGroup.add_argument("--LHE", action='store_true', help="LHE events + Pythia")

from math import pi
singlePartGroup = simparser.add_argument_group('Single particles')
singlePartGroup.add_argument('-e','--energy', type=int, required = True, help='Energy of particle in GeV')
singlePartGroup.add_argument('--etaMin', type=float, default=0., help='Minimal pseudorapidity')
singlePartGroup.add_argument('--etaMax', type=float, default=0., help='Maximal pseudorapidity')
singlePartGroup.add_argument('--phiMin', type=float, default=0, help='Minimal azimuthal angle')
singlePartGroup.add_argument('--phiMax', type=float, default=2*pi, help='Maximal azimuthal angle')
singlePartGroup.add_argument('--particle', type=int,  required = True, help='Particle type (PDG)')

pythiaGroup = simparser.add_argument_group('Pythia','Common for min bias and LHE')
pythiaGroup.add_argument('-c', '--card', type=str, default='PythiaCards/default.cmd', help='Path to Pythia card (default: PythiaCards/default.cmd)')

lheGroup = simparser.add_argument_group('LHE','Additional for generation with LHE')
lheGroup.add_argument('--process', type=str, help='Event type [Zee, Haa, Hbb, Wqq, Zqq, t, ljet]')
lheGroup.add_argument('--pt', type=int, help='Transverse momentum of simulated jets')
simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
magnetic_field = not simargs.bFieldOff
num_events = simargs.numEvents
seed = simargs.seed
output_name = simargs.output
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
elif simargs.minBias:
    card = simargs.card
    print "=================================="
    print "==           MIN BIAS          ==="
    print "=================================="
    print "card = ", card
elif simargs.LHE:
    card = simargs.card
    lhe_type = simargs.process
    pt = simargs.pt
    print "=================================="
    print "==             LHE             ==="
    print "=================================="
    print "card: ", card
    print "LHE type: ", lhe_type
    print "jet pt: ", pt
print "=================================="


# from Gaudi.Configuration import *
# from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput
# podioevent = FCCDataSvc("EventDataSvc")

# from Configurables import GeoSvc
# geoservice = GeoSvc("GeoSvc", detectors=[  'file:Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
#                                            'file:Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
#                                            'file:Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_'+geometry+'.xml',
#                                            'file:Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml',
#                                            'file:Detector/DetFCChhCalDiscs/compact/Forward_coneCryo.xml' ],
#                     OutputLevel = INFO)

# from Configurables import SimG4Svc
# geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist="SimG4FtfpBert", actions="SimG4FullSimActions")
# #Setting random seeds for Geant4 simulations
# geantservice.g4PostInitCommands += ["/random/setSeeds "+str(seed_array[part-1])+" 0"]

# #range cut
# geantservice.g4PostInitCommands += ["/run/setCut 0.1 mm"]

# from Configurables import SimG4Alg, SimG4SaveCalHits, SimG4SingleParticleGeneratorTool
# saveecaltool = SimG4SaveCalHits("saveECalBarrelHits",readoutNames = ["ECalBarrelEta"])
# saveecaltool.positionedCaloHits.Path = "ECalBarrelPositionedHits"
# saveecaltool.caloHits.Path = "ECalBarrelHits"
# savecalendcaptool = SimG4SaveCalHits("saveECalEndcapHits", readoutNames = ["EMECPhiEta"])
# savecalendcaptool.positionedCaloHits.Path = "ECalEndcapPositionedHits"
# savecalendcaptool.caloHits.Path = "ECalEndcapHits"
# savecalfwdtool = SimG4SaveCalHits("saveECalFwdHits", readoutNames = ["EMFwdPhiEta"])
# savecalfwdtool.positionedCaloHits.Path = "ECalFwdPositionedHits"
# savecalfwdtool.caloHits.Path = "ECalFwdHits"

# from Configurables import SimG4SingleParticleGeneratorTool
# pgun=SimG4SingleParticleGeneratorTool("SimG4SingleParticleGeneratorTool",saveEdm=True,
#                                       particleName=particleName,energyMin=energy * 1000,energyMax=energy * 1000,
#                                       etaMin=eta, etaMax=eta,
#                                       OutputLevel =DEBUG)

# # Magnetic field
# from Configurables import SimG4ConstantMagneticFieldTool
# if magnetic_field==1:
#     field = SimG4ConstantMagneticFieldTool("SimG4ConstantMagneticFieldTool",FieldOn=True,IntegratorStepper="ClassicalRK4")
# else:
#     field = SimG4ConstantMagneticFieldTool("SimG4ConstantMagneticFieldTool",FieldOn=False)
# geantsim = SimG4Alg("SimG4Alg",
#                     outputs= ["SimG4SaveCalHits/saveECalBarrelHits", "SimG4SaveCalHits/saveECalEndcapHits", "SimG4SaveCalHits/saveECalFwdHits"],
#                     eventProvider = pgun)

# #Configure tools for calo reconstruction
# from Configurables import CalibrateInLayersTool
# calibcellsBarrel = CalibrateInLayersTool("CalibrateBarrel",
#                                    # sampling fraction obtained using SamplingFractionInLayers from DetStudies package
#                                    samplingFraction = [0.12125] + [0.14283] + [0.16354] + [0.17662] + [0.18867] + [0.19890] + [0.20637] + [0.20802],
#                                    readoutName = "ECalBarrelEta",
#                                    layerFieldName = "layer")
# calibcellsEndcap = CalibrateInLayersTool("CalibrateEndcap",
#                                          # sampling fraction obtained using SamplingFractionInLayers from DetStudies package
#                                     samplingFraction = [0.057373] * 156,
#                                     readoutName = "EMECPhiEta",
#                                     layerFieldName = "layer")
# calibcellsFwd = CalibrateInLayersTool("CalibrateFwd",
#                                          # sampling fraction obtained using SamplingFractionInLayers from DetStudies package
#                                     samplingFraction = [0.0519] * 48,
#                                     readoutName = "EMFwdPhiEta",
#                                     layerFieldName = "layer")

# from Configurables import CreateCaloCells
# createcellsBarrel = CreateCaloCells("CreateCaloCellsBarrel",
#                                     doCellCalibration=True,
#                                     calibTool=calibcellsBarrel,
#                                     addCellNoise=False, filterCellNoise=False,
#                                     OutputLevel=DEBUG)
# createcellsBarrel.hits.Path="ECalBarrelHits"
# createcellsBarrel.cells.Path="ECalBarrelCellsNoPhi"
# createcellsEndcap = CreateCaloCells("CreateCaloCellsEndcap",
#                                     doCellCalibration=True,
#                                     calibTool=calibcellsEndcap,
#                                     addCellNoise=False, filterCellNoise=False,
#                                     OutputLevel=DEBUG)
# createcellsEndcap.hits.Path="ECalEndcapHits"
# createcellsEndcap.cells.Path="ECalEndcapCells"
# createcellsFwd = CreateCaloCells("CreateCaloCellsFwd",
#                                     doCellCalibration=True,
#                                     calibTool=calibcellsFwd,
#                                     addCellNoise=False, filterCellNoise=False,
#                                     OutputLevel=DEBUG)
# createcellsFwd.hits.Path="ECalFwdHits"
# createcellsFwd.cells.Path="ECalFwdCells"

# # Retrieve phi positions from centres of cells
# from Configurables import CreateVolumeCaloPositions
# positionsEcalBarrel = CreateVolumeCaloPositions("positionsEcalBarrel", OutputLevel = INFO)
# positionsEcalBarrel.hits.Path = "ECalBarrelCellsNoPhi"
# positionsEcalBarrel.positionedHits.Path = "ECalBarrelPositions"
# from Configurables import RedoSegmentation
# resegmentEcal = RedoSegmentation("ReSegmentationEcalBarrel",
#                              oldReadoutName = 'ECalBarrelEta',
#                              oldSegmentationIds = ['module'],
#                              newReadoutName = 'ECalBarrelPhiEta',
#                              inhits = "ECalBarrelPositions",
#                              outhits = "ECalBarrelCells")


# #Create calo clusters
# from Configurables import CreateCaloClustersSlidingWindow, SingleCaloTowerTool
# from GaudiKernel.PhysicalConstants import pi
# towers = SingleCaloTowerTool("towers",
#                              deltaEtaTower = 0.01, deltaPhiTower = 2*pi/704.,
#                              readoutName = "ECalBarrelPhiEta",
#                              OutputLevel = DEBUG)
# towers.cells.Path="ECalBarrelCells"

# createclusters = CreateCaloClustersSlidingWindow("CreateCaloClusters",
#                                                  towerTool = towers,
#                                                  nEtaWindow =7, nPhiWindow = 15,
#                                                  nEtaPosition = 3, nPhiPosition = 3,
#                                                  nEtaDuplicates = 5, nPhiDuplicates = 7,
#                                                  nEtaFinal = 7, nPhiFinal = 17,
#                                                  energyThreshold = 3,
#                                                  OutputLevel = DEBUG)
# createclusters.clusters.Path = "ECalClusters"

# # PODIO algorithm
# from Configurables import PodioOutput
# out = PodioOutput("out",
#                    OutputLevel=DEBUG)
# out.outputCommands = ["drop *", "keep GenParticles", "keep GenVertices", "keep ECalBarrelCells", "keep ECalEndcapCells", "keep ECalFwdCells", "keep ECalClusters"]
# out.filename = "sim_ecal_"+particle+str(energy)+"GeV_eta"+str(eta)+"_Bfield"+str(magnetic_field)+"_"+geometry+"_"+str(num_events)+"events_part"+str(part)+".root"

# #CPU information
# from Configurables import AuditorSvc, ChronoAuditor
# chra = ChronoAuditor()
# audsvc = AuditorSvc()
# audsvc.Auditors = [chra]
# geantsim.AuditExecute = True
# createcellsBarrel.AuditExecute = True
# createcellsEndcap.AuditExecute = True
# createcellsFwd.AuditExecute = True
# positionsEcalBarrel.AuditExecute = True
# resegmentEcal.AuditExecute = True
# createclusters.AuditExecute = True
# out.AuditExecute = True

# ApplicationMgr(
#     TopAlg = [geantsim,
#               createcellsBarrel,
#               createcellsEndcap,
#               createcellsFwd,
#               positionsEcalBarrel,
#               resegmentEcal,
#               createclusters,
#               out
#               ],
#     EvtSel = 'NONE',
#     EvtMax   = num_events,
#     ExtSvc = [podioevent, geoservice],
#  )

