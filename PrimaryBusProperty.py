from PciProperty import PciProperty


class PrimaryBusProperty(PciProperty):


    def get_with_CRspace(self): #port 0 only !
        return self.Property_resurces.get_CRspace_agent().mst_read('primary_bus')

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        pass

    def set_with_CliAgent(self, value):
        pass






