import feature
from Monostate import Monostate
from prettytable import PrettyTable


class PrintSetupInfoFeature(feature.feature):
    def __init__(self):
        self.server = Monostate()

    def print_feature(self):
        SetupTtable = PrettyTable()
        SetupTtable.field_names = ["Device","Device name", "BDF" , "Cr-space","Secure FW","Is dut","Is switch"]
        USC_component=self.server.getUscComponent()
        Device_name,BDF,CrSpace,SecureFW,isSwitch=self.getdataFromMonostate(USC_component)
        SetupTtable.add_row(["USC component",str(Device_name),str(BDF) ,str(CrSpace),str(SecureFW),self.server._inner.dutIsUpstream,str(isSwitch)])

        DSC_component = self.server.getDscComponent()
        Device_name, BDF, CrSpace, SecureFW, isSwitch = self.getdataFromMonostate(DSC_component)
        SetupTtable.add_row(["DSC component", str(Device_name), str(BDF), str(CrSpace), str(SecureFW),
                             not self.server._inner.dutIsUpstream, str(isSwitch)])

        print(SetupTtable)

    def getdataFromMonostate(self,component):
        SecureFW=component.resources.CR_space_agent.get_read_only_flag()
        CrSpace=component.resources.CR_space_agent.get_CRspace()
        BDF=component.resources.conf_space_agent.get_bdf()
        Device_name=component.getDeviceName()
        isSwitch=component.getIsSwitch()
        return Device_name,BDF,CrSpace,SecureFW,isSwitch




