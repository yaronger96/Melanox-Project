from PciProperty import PciProperty


class PxdCauseProperty(PciProperty):
    def get_with_CRspace(self):

        return self.Property_resurces.get_CRspace_agent().mst_read('pxd_cause_get')



    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        pass

    def get_with_CliAgent(self):
        pass

    def set_with_CRspace(self, value):
        pass

    def set_with_Confspace(self, value):
        pass
    def set_with_CliAgent(self, value):
        pass




