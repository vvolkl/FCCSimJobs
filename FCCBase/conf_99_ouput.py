
import uuid
from Configurables import PodioOutput

out = PodioOutput("out")
out.filename = "events_" +  uuid.uuid4().hex + ".root"
out.outputCommands = [
                      "keep *",
                      ]
from Configurables import ApplicationMgr
ApplicationMgr().TopAlg += [out]
