from PciProperty import PciProperty


class SpeedProperty(PciProperty):

    def get_with_CRspace(self):
        return self.Property_resurces.get_CRspace_agent().mst_read('current_link_speed')

    def get_with_Confspace(self): ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_speed = ConfSpace_agent.read(0x10, False, 0x12, 0, 4)
        return link_speed

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        update_speed = self.Property_resurces.get_CRspace_agent().mst_write('speed_en', hex(value))
        self.Property_resurces.get_CRspace_agent().mst_write('fw_directed_speed_change', hex(value))
        return update_speed

    def set_with_Confspace(self, value):
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        link_target_updated = ConfSpace_agent.write(0x10, False, 0x30, 0, 4, hex(value))
        retrain_link = ConfSpace_agent.write(0x10, False, 0x10, 5, 1, 1) ######chang !
        return link_target_updated  #return the value in the reg after the change

    def set_with_CliAgent(self, value):
        pass






