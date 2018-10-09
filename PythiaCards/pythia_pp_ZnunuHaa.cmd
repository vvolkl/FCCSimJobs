! 1) Settings used in the main program.
Main:numberOfEvents = 1000         ! number of events to generate
Main:timesAllowErrors = 100        ! how many aborts before run stops
Random:setSeed = on
Random:seed = 0

! 2) Settings related to output in init(), next() and stat().
Init:showChangedSettings = on      ! list changed settings
Init:showChangedParticleData = off ! list changed particle data
Next:numberCount = 100             ! print message every n events
Next:numberShowInfo = 1            ! print event information n times
Next:numberShowProcess = 1         ! print process record n times
Next:numberShowEvent = 0           ! print event record n times

ParticleDecays:tau0Max = 10        ! ... if c*tau0 > 10 mm
ParticleDecays:limitCylinder = on
ParticleDecays:xyMax = 20          ! mm
ParticleDecays:zMax = 30000        ! mm, (full extent of beampipe)

####################
######SPECIFIC######
####################
Beams:idA = 2212                   ! first beam, p = 2212, pbar = -2212
Beams:idB = 2212                   ! second beam, p = 2212, pbar = -2212
Beams:eCM = 100000.                ! CM energy of collision


HiggsSM:ffbar2HZ = on
23:onMode = off
25:onMode = off
25:onIfAny = 22
23:onIfAny = 14 16 18

PartonLevel:MPI = on 

PhaseSpace:pTHatMin = 200
