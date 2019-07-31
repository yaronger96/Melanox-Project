import Monostate
import DisableEnableProperty
import SpeedProperty
from Operation import Operation
import time


class DisableEnableOp(Operation):
    def __init__(self):
        Operation.__init__(self)
        self.server = Monostate.Monostate()

    def execute(self):
        usc = self.server._inner.upstreamComponent
        valid = self.checkGenOp()
        if not valid:
            print "Speed must be gen 3 & above, exiting.."
            exit(1)
        disableenableprop = DisableEnableProperty.DisableEnableProperty(usc.resources)
        disableenableprop.set_with_Confspace(1)
        time.sleep(0.05)
        disableenableprop.set_with_Confspace(0)
        time.sleep(0.32)
        if usc.isSwitch():
            self.rescanPciBuses()

    def checkGenOp(self):
        usc = self.server._inner.upstreamComponent
        speedProp = SpeedProperty.SpeedProperty(usc.resources)
        currentSpeed = speedProp.get()
        if currentSpeed < 3:
            return False
        return True
