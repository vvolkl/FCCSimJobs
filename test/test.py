

# use common config (order is important!)
from FCCBase.conf_00_main import *
from FCCBase.conf_10_particlegun import *
# pick  and choose modules
#from FCCBase.conf_20_det import *
#from FCCBase.conf_30_sim import *
from FCCBase.conf_32_sim_randomseed import randomEngine
from FCCBase.conf_99_ouput import *

# change a single options
randomEngine.Seeds = [4444]
# changing properties of private tools is slightly awkward
# important to do it via the algorithm that owns it
GenAlg().SignalProvider.PdgCodes = [14]

# set number of Events
ApplicationMgr().EvtMax = 1000




