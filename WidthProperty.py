from PciProperty import PciProperty


class WidthProperty(PciProperty):

    def get_with_CRspace(self):
        return self.Property_resurces.get_CRspace_agent().mst_read('negotiated_link_width')

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




