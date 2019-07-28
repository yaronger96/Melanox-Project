from PciProperty import PciProperty


class VendorIDProperty(PciProperty):
    def __init__(self,resource):
        PciProperty.__init__(self, resource)
        self.device_vendor_id = None

    def get_with_CRspace(self):
        pass

    def get_with_Confspace(self):
        return self.Property_resurces.get_CRspace_agent().mst_read('vendor_id')

    def get_with_CliAgent(self):
        pass

    def is_mlx_device(self):
        print self.device_vendor_id
        if self.device_vendor_id == hex(0x15b3):
            return True
        return False
