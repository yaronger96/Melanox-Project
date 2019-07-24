from PciProperty import PciProperty


class DisableEnableProperty(PciProperty):

    def get_with_CRspace(self):
        pass


    def get_with_Confspace(self):
        return self.Property_resurces.get_Confspace_agent().read('link disable')

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        # return the value in the reg after the change
        return self.Property_resurces.get_Confspace_agent().write('link disable', hex(value))

    def set_with_CliAgent(self, value):
        pass






