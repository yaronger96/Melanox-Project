from PciProperty import PciProperty


class CauseBulkProperty(PciProperty):
    def __init__(self, resurces,nameOfReg):
        PciProperty.__init__(self, resurces)
        self.nameOfReg = nameOfReg
    def get_with_CRspace(self):
        return self.Property_resurces.get_CRspace_agent().mst_read(self.nameOfReg)



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




