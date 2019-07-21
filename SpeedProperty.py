from PciProperty import PciProperty


class SpeedProperty(PciProperty):

    def get_with_CRspace(self):
        device, address, offset, size = self.getDataFromCrspaceDb('current_link_speed')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        jump_between_port = self.get_speed_jump()
        if self.getPcoreNum() is None:
            address += jump_between_port * self.Property_resurces.CR_space_agent.getPortNumber()
        else:
            mod = self.getModAccordingPcoreNum()
            address += jump_between_port * (self.Property_resurces.CR_space_agent.getPortNumber() % mod)
        return self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)


    def get_speed_jump(self): ##### the device,address,size not use
        device, address, jump, size = self.getDataFromCrspaceDb('jump_between_current_link_speed')
        if jump is 'error':
            return 0 #if i dint have the data about the jump I dont jump
        return jump

    def get_with_Confspace(self): ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_speed = ConfSpace_agent.read(0x10, False, 0x12, 0, 4)
        return link_speed

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        device, address, offset, size = self.getDataFromCrspaceDb('speed_en')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        jump_between_port = self.get_speed_jump()
        if self.getPcoreNum() is None:
            address += jump_between_port * self.Property_resurces.CR_space_agent.getPortNumber()
        else:
            mod = self.getModAccordingPcoreNum()
            address += jump_between_port * (self.Property_resurces.CR_space_agent.getPortNumber() % mod)
        update_speed = self.Property_resurces.get_CRspace_agent().mst_write(device, address, hex(value), offset, size)
        device, address, offset, size = self.getDataFromCrspaceDb('fw_directed_speed_change')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        if self.getPcoreNum() is None:
            address += jump_between_port * self.Property_resurces.CR_space_agent.getPortNumber()
        else:
            mod = self.getModAccordingPcoreNum()
            address += jump_between_port * (self.Property_resurces.CR_space_agent.getPortNumber() % mod)
        self.Property_resurces.get_CRspace_agent().mst_write(device, address, hex(value), offset, size)
        return update_speed

    def set_with_Confspace(self, value):
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_target_updated = ConfSpace_agent.write(0x10, False, 0x30, 0, 4, hex(value))
        retrain_link = ConfSpace_agent.write(0x10, False, 0x10, 5, 1, 1) ######chang !
        return link_target_updated  #return the value in the reg after the change

    def set_with_CliAgent(self, value):
        pass






def main():
    leep=SpeedProperty(1233490)
    print leep.get_with_CRspace()
    #print "current Link speed", link_speed, ("PASSED" if int(speed) == int(link_speed, 16) else "FAILED")

if __name__=='__main__':
    main()
