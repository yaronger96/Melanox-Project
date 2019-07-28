from PciProperty import PciProperty


class WidthProperty(PciProperty):

    def get_with_CRspace(self):
        return self.Property_resurces.get_CRspace_agent().mst_read('negotiated_link_width')

    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        return self.Property_resurces.get_CRspace_agent().read('negotiated link width')

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        return self.Property_resurces.get_CRspace_agent().write('negotiated link width',hex(value))


    def set_with_CliAgent(self, value):
        pass




