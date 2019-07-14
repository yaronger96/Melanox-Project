from Monostate import Monostate
from DisableEnableProperty import DisableEnableProperty
from Operation import Operation
import time

class DisableEnableOp(Operation):
    def execute(self):
        server = Monostate()
        usc = server._inner.upstreamComponent
        dsc = server._inner.downstreamComponent
        disableenableprop = DisableEnableProperty(usc.resources)
        disableenableprop.set_with_Confspace(1)
        time.sleep(0.1)
        disableenableprop.set_with_Confspace(0)
        if usc.isSwitch():
            self.rescanPciBuses()





