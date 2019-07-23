from PciProperty import PciProperty


class RxErrorProperty(PciProperty):
    def get_with_CRspace(self):
        # device, address, offset, size = self.getDataFromCrspaceDb('rx_errors_get')
        # if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
        #     print "error with get the data from CR_space"
        # jump_between_port = self.get_RxError_jump()
        # if self.getPcoreNum() is None:
        #     address += jump_between_port * self.Property_resurces.CR_space_agent.getPortNumber()
        # else:
        #     mod = self.getModAccordingPcoreNum()
        #     address += jump_between_port * (self.Property_resurces.CR_space_agent.getPortNumber() % mod)
        return self.Property_resurces.get_CRspace_agent().mst_read('rx_errors_get')



    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        pass

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        pass
    def set_with_CliAgent(self, value):
        pass




