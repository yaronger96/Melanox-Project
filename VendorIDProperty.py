from PciProperty import PciProperty


class VendorIDProperty(PciProperty):
    def __init__(self,resource):
        PciProperty.__init__(self, resource)
        self.device_vendor_id = None

    def get_with_CRspace(self):
        pass

    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        self.device_vendor_id = ConfSpace_agent.read_header(0x00, 0, 16)
        return self.device_vendor_id

    def get_with_CliAgent(self):
        pass

    def is_mlx_device(self):
        print self.device_vendor_id
        if self.device_vendor_id == hex(0x15b3):
            return True
        return False
