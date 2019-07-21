from PciProperty import PciProperty


class CompliterIdProperty(PciProperty):
    def __init__(self, resource, portNumber=0):
        PciProperty.__init__(self, resource)
        self.portNumber = portNumber

    def get_with_CRspace(self):
        device, address, offset, size = self.getDataFromCrspaceDb('cfgwr0_compliter_id')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        jump_between_port = self.get_compliter_id_jump()
        if self.getPcoreNum() is None:
            address += jump_between_port * self.portNumber
        else:
            mod = self.getModAccordingPcoreNum()
            address += jump_between_port * (self.portNumber % mod)
        return self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)

    def get_compliter_id_jump(self): ##### the device,address,size not use
        device, address, jump, size = self.getDataFromCrspaceDb('jump_between_compliter')
        if jump is 'error':
            return 0 #if i dint have the data about the jump I dont jump
        return jump

    def set_port_number(self, portNumber):
        self.portNumber = portNumber


    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        pass

    def set_with_CliAgent(self, value):
        pass






def main():
    leep=SpeedProperty(1233490)
    print leep.get_with_CRspace()
    #print "current Link speed", link_speed, ("PASSED" if int(speed) == int(link_speed, 16) else "FAILED")

if __name__=='__main__':
    main()
