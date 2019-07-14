import feature
from PciResurces import PciResurces


class PciComponent(feature.feature):
    def __init__(self):
        self.resources = PciResurces()
        self.isSwitch = None
        self.deviceName = None

    def getResourcse(self):
        return self.resources

    def getIsSwitch(self):
        return self.isSwitch

    def getDeviceName(self):
        return self.deviceName

    def setResources(self,resources):
        self.resources = resources

    def setIsSwitch(self,isSwitch):
        self.isSwitch = isSwitch

    def setDeviceName(self,deviceName):
        self.deviceName = deviceName

    def print_feature(self):
        print "This is {} device".format(self.deviceName)


usc = PciComponent()


