from PciProperty import PciProperty


class PrimaryBusProperty(PciProperty):


    def get_with_CRspace(self): #port 0 only !
        # device, address, offset, size = self.getDataFromCrspaceDb('primary_bus')
        # if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
        #     print "error with get the data from CR_space"

        # if self.getPcoreNum() is None:
        #     address += jump_between_port * self.portNumber
        # else:
        #     mod = self.getModAccordingPcoreNum()
        #     address += jump_between_port * (self.portNumber % mod)
        return self.Property_resurces.get_CRspace_agent().mst_read('primary_bus')

    # def get_p_jump(self): ##### the device,address,size not use
    #     device, address, jump, size = self.getDataFromCrspaceDb('jump_between_compliter')
    #     if jump is 'error':
    #         return 0 #if i dint have the data about the jump I dont jump
    #     return jump

    # def set_port_number(self, portNumber):
    #     self.portNumber = portNumber


    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        pass

    def set_with_CliAgent(self, value):
        pass






