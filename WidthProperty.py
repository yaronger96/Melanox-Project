from PciProperty import PciProperty


class WidthProperty(PciProperty):

    def get_with_CRspace(self):
        device, address, offset, size = self.getDataFromCrspaceDb('negotiated_link_width')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        jump_between_port = self.get_speed_jump()
        if self.getPcoreNum() is None:
            address += jump_between_port * self.Property_resurces.CR_space_agent.getPortNumber()
        else:
            mod = self.getModAccordingPcoreNum()
            address += jump_between_port * (self.Property_resurces.CR_space_agent.getPortNumber() % mod)
        return self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)

    def get_width_jump(self): ##### the device,address,size not use
        device, address, jump, size = self.getDataFromCrspaceDb('jump_between_negotiated_link_width')
        if jump is 'error':
            return 0 #if i dint have the data about the jump I dont jump
        return jump


    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        return ConfSpace_agent.read(0x10, False, 0x12, 4, 6)

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        pass
        # ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        # link_target_updated = ConfSpace_agent.write(0x10, False, 0x12, 4, 6, hex(value))
        # return link_target_updated  # return the value in the reg after the change

    def set_with_CliAgent(self, value):
        pass




