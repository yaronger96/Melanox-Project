from PciProperty import PciProperty


class SpeedProperty(PciProperty):

    def get_with_CRspace(self):
        device, address, offset, size = self.getDataFromCrspaceDb('current_link_speed')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        return self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)


    def get_with_Confspace(self): ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_speed = ConfSpace_agent.read(0x10, False, 0x12, 0, 4)
        return link_speed

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        device, address, offset, size = self.getDataFromCrspaceDb('?????????????????????????')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        return self.Property_resurces.get_CRspace_agent().mst_write(device, address, int(value), offset, size)

    def set_with_Confspace(self, value):
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_target_updated = ConfSpace_agent.write(0x10, False, 0x30, 0, 4, int(value))
        return link_target_updated  #return the value in the reg after the change

    def set_with_CliAgent(self, value):
        pass






def main():
    leep=SpeedProperty(1233490)
    print leep.get_with_CRspace()
    #print "current Link speed", link_speed, ("PASSED" if int(speed) == int(link_speed, 16) else "FAILED")

if __name__=='__main__':
    main()
