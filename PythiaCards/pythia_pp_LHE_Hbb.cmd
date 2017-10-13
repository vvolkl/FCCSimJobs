! main03.cmnd.
! This file contains commands to be read in for a Pythia8 run.
! Lines not beginning with a letter or digit are comments.
! Names are case-insensitive  -  but spellings-sensitive!
! The settings here are illustrative, not always physics-motivated.

! 1) Settings used in the main program.
Random:setSeed = on
Random:seed = 0

Main:numberOfEvents = 1000         ! number of events to generate
Main:timesAllowErrors = 100         ! how many aborts before run stops

! 2) Settings related to output in init(), next() and stat().
Init:showChangedSettings = on      ! list changed settings
Init:showChangedParticleData = off ! list changed particle data
Next:numberCount = 100             ! print message every n events
Next:numberShowInfo = 1            ! print event information n times
Next:numberShowProcess = 1         ! print process record n times
Next:numberShowEvent = 0           ! print event record n times

! 4) Read-in Les Houches Event file - alternative beam and process selection.
Beams:frameType = 4                      ! read info from a LHEF
#Beams:LHEF = events.lhe ! the LHEF to read from

25:onIfAny = 5


ParticleDecays:tau0Max = 10        ! ... if c*tau0 > 10 mm
ParticleDecays:limitCylinder = on
ParticleDecays:xyMax = 20          ! mm
ParticleDecays:zMax = 30000        ! mm, (full extent of beampipe)

