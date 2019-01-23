
from Gaudi.Configuration import * 

from Configurables import ApplicationMgr
main = ApplicationMgr()
main.EvtSel = 'NONE'
main.EvtMax = 10
main.TopAlg = []
main.ExtSvc = []

# PODIO algorithm
from Configurables import FCCDataSvc
podioevent = FCCDataSvc("EventDataSvc")
main.ExtSvc += [podioevent]




