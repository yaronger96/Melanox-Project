from PciProperty import PciProperty


class HotResetProperty(PciProperty):

    def get_with_CRspace(self):
        pass


    def get_with_Confspace(self): ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        hot_reset = ConfSpace_agent.read(0x3E, False, 0x3E, 6, 1)
        return hot_reset

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        updated_flag = ConfSpace_agent.write(0x3E, False, 0x3E, 6, 1, hex(value))
        return updated_flag  #return the value in the reg after the change

    def set_with_CliAgent(self, value):
        pass






def main():
    leep=SpeedProperty(1233490)
    print leep.get_with_CRspace()
    #print "current Link speed", link_speed, ("PASSED" if int(speed) == int(link_speed, 16) else "FAILED")

if __name__=='__main__':
    main()
