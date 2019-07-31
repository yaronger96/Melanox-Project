import Monostate
from SpeedProperty import SpeedProperty
from Operation import Operation
import time


class SpeedChangeOp(Operation):

    def __init__(self):
        Operation.__init__(self)
        self.server = Monostate.Monostate()

    def execute(self, targetspeed):
        usc = self.server._inner.upstreamComponent
        speedchangeprop = SpeedProperty(usc.resources)
        currentspeed = speedchangeprop.get_with_Confspace()
        print "Changing from Gen {} to Gen {}".format(currentspeed, targetspeed)
        speedchangeprop.set_with_Confspace(targetspeed)
        time.sleep(0.1) ####change




