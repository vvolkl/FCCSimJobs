
from FCCBase.conf_00_main import *
from FCCBase.conf_10_particlegun import *
#from FCCBase.conf_20_det import *
#from FCCBase.conf_30_sim import *
from FCCBase.conf_32_sim_randomseed import randomEngine
from FCCBase.conf_99_ouput import *

randomEngine.Seeds = [4444]
GenAlg().SignalProvider.PdgCodes = [14]




