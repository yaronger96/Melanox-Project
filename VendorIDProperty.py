from PciProperty import PciProperty


class VendorIDProperty(PciProperty):
    def __init__(self):
        self.device_vendor_id = None

    def get_with_CRspace(self):
        device, address, offset, size = self.getDataFromCrspaceDb('????????????????????')
        if device is 'error' & address is 'error' & offset is 'error' & size is 'error':
            print "error with get the data from CR_space"
        status,self.device_vendor_id=self.Property_resurces.get_CRspace_agent().mst_read(device, address, offset, size)
        return status,self.device_vendor_id

    def get_with_Confspace(self):  ##### maybee need to casting to hex !!!!
        ConfSpace_agent = self.Property_resurces.get_Confspace_agent()
        status,self.device_vendor_id= ConfSpace_agent.read_header(0x00, 0, 16)
        return  status,self.device_vendor_id

    def get_with_CliAgent(self):
        pass

    def is_mlx_device(self):
        if str(self.device_vendor_id) == '15b3':
            return True
        return False






