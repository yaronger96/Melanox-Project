from PciProperty import PciProperty

class HeaderTypeProperty(PciProperty):

    #     def get_with_CRspace(self):
    #         device, address, offset, size = self.getDataFromCrspaceDb('????????????????????')
    #         if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
    #             print "error with get the data from CR_space"
    #         return self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)

    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        return self.Property_resurces.get_Confspace_agent().read('header type')

    def get_with_CliAgent(self):
        pass
