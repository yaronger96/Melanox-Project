from PciProperty import PciProperty


class DisableEnableProperty(PciProperty):

    def get_with_CRspace(self):
        pass


    def get_with_Confspace(self): ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_disable = ConfSpace_agent.read(0x10, False, 0x10, 4, 1)
        return link_disable

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_disable_updated = ConfSpace_agent.write(0x10, False, 0x10, 4, 1, hex(value))
        return link_disable_updated  #return the value in the reg after the change

    def set_with_CliAgent(self, value):
        pass






def main():
    leep=SpeedProperty(1233490)
    print leep.get_with_CRspace()
    #print "current Link speed", link_speed, ("PASSED" if int(speed) == int(link_speed, 16) else "FAILED")

if __name__=='__main__':
    main()
