#!/usr/bin/env gaudirun.py

from Configurables import *


import sys
print sys.argv[1]

# use common config (order is important!)
from FCCBase.conf_00_main import *
from FCCBase.conf_10_particlegun import *
# pick  and choose modules
#from FCCBase.conf_20_det import *
#from FCCBase.conf_30_sim import *
#from FCCBase.conf_32_sim_randomseed import randomEngine
from FCCBase.conf_99_ouput import *

# change a single options
#randomEngine.Seeds = [4444]
# changing properties of private tools is slightly awkward
# important to do it via the algorithm that owns it
GenAlg().SignalProvider.PdgCodes = [15] 
GenAlg().SignalProvider.EtaMin = "-4.0" 

# set number of Events
ApplicationMgr().EvtMax = "12"
ApplicationMgr().OutputLevel = INFO
genfilter.OutputLevel =INFO




