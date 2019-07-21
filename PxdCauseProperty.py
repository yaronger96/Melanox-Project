from PciProperty import PciProperty


class PxdCauseProperty(PciProperty):
    def get_with_CRspace(self):
        device, address, offset, size = self.getDataFromCrspaceDb('pxd_cause_get')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        jump_between_port = self.get_compliter_id_jump()
        if self.getPcoreNum() is None:
            address += jump_between_port * self.Property_resurces.CR_space_agent.getPortNumber()
        else:
            mod = self.getModAccordingPcoreNum()
            address += jump_between_port * (self.Property_resurces.CR_space_agent.getPortNumber() % mod)
        return self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)

    def get_compliter_id_jump(self): ##### the device,address,size not use
        device, address, jump, size = self.getDataFromCrspaceDb('jump_between_pxd_cause_get')
        if jump is 'error':
            return 0 #if i dint have the data about the jump I dont jump
        return jump

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




