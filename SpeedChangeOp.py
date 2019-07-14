from Monostate import Monostate
from SpeedProperty import SpeedProperty
from Operation import Operation
import time


class SpeedChangeOp(Operation):
    def execute(self, targetspeed):
        server = Monostate()
        usc = server._inner.upstreamComponent
        dsc = server._inner.downstreamComponent
        speedchangeprop = SpeedProperty(usc.resources)
        currentspeed = speedchangeprop.get_with_Confspace()
        print "Changing from Gen {} to Gen {}".format(currentspeed, targetspeed)
        speedchangeprop.set_with_Confspace(targetspeed)
        time.sleep(0.1)




