from PciProperty import PciProperty

class HeaderTypeProperty(PciProperty):

    #     def get_with_CRspace(self):
    #         device, address, offset, size = self.getDataFromCrspaceDb('????????????????????')
    #         if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
    #             print "error with get the data from CR_space"
    #         return self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)

    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        header_type = ConfSpace_agent.read_header(0x0E, 0, 7)
        return header_type

    def get_with_CliAgent(self):
        pass
