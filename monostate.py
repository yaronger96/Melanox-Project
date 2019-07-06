import os
import re
import cli_agent
import CR_space_agent
import  conf_space_agent
import PciComponent
import HeaderTypeProperty



#######################data ####################
device_cr_space={ ##key =device ID , value= CR_space_name
    4119 : "/dev/mst/mt4119_pciconf0 ",
    4117 : "/dev/mst/mt4117_pciconf0"
}

device_name={ ##key =device ID , value= CR_space_name
    "mt4119_pciconf0" : "BW",
    "mt4117_pciconf0" : "Connect_x_5"

}



#################################################
class Monostate:
    _inner = None
    class inner:
        def __init__(self):
            self.serverName = None
            self.dut = None
            self.dutType = None
            self.dutIsUpstream = None
            self.mlxDut = None
            self.os = None
            self.resources = dict()
            self.dutHasSecureFw = None
            self.dutComponent = None     # pci component
            self.rootPortComponent = None
            self.upstreamComponent = None # pci component
            self.downstreamComponent = None # pci component
            self.CliAgent=None

    def __init__(self,dut="",serverName = "Local"):
        if Monostate._inner is None:
            Monostate._inner = Monostate.inner()
         ##   monostate._inner.dut = dut
            self.dut=dut
            Monostate.evalDutType()
            Monostate.evalServerName(serverName)
            self.dutComponent = PciComponent()
            self.upstreamComponent = PciComponent()
            self.downstreamComponent = PciComponent()
            if(self.dutTtpe == "BDF Device"):
                self.init_BDF_Device_input()
            elif (self.dutTtpe == "CRspace Device"):
                self.init_CRspace_Device_input()
            elif (self.dutTtpe == "MTusb Device"):
                self.init_MtUsb_input()
            print("monostate done")




    def evalDutType(self):
        if ":" in Monostate._inner.dut:
           Monostate._inner.dutType = "BDF Device"
        elif "mst_dev" in Monostate._inner.dut:
            Monostate._inner.dutType = "CRspace Device"
        elif "MTusb" in Monostate._inner.dut:
            Monostate._inner.dutType = "MTusb Device"
        else:
            Monostate._inner.dutType = "Unknown Device"



    def evalServerName(self, serverName):
        if serverName is not "Local":
            Monostate._inner.serverName = "Remote"
            Monostate._inner.CliAgent = cli_agent.CLiAgentRemote(serverName)
        else:
            Monostate._inner.serverName = "Local"
            Monostate._inner.CliAgent = cli_agent.CliAgentLocal()


    def init_MtUsb_input(self):
        Monostate._inner.mlxDut = '1'
        Monostate._inner.dutComponent.CR_space = CR_space_agent()

    def init_BDF_Device_input(self):
        Monostate._inner.dutComponent.BDF = Monostate._inner.dut
        Monostate._inner.dutComponent.conf_space = conf_space_agent()
        self.find_cr_space(Monostate._inner.dutComponent.BDF, "dut")
        # now we have all the information about the dut
        self.find_topology()

    def init_CRspace_Device_input(self):
        Monostate._inner.mlxDut = '1'
        Monostate._inner.dutComponent.CR_space = CR_space_agent()
        input=Monostate._inner.dut.split("/")
        self.find_BDF_according_the_device(input[2]) ##the device_number
        #now we have all the information about the dut
        self.find_topology()

    def find_cr_space(self , BDF , name_of_component):
        temp="set pci -s" + str(BDF) + "00"
        while True:
            vendor_ID = Monostate._inner.CliAgent.exec_command(temp) ##command->set pci -s BDF 00 vendorID
            if(vendor_ID != 1) :##if 1 =error
                break
            print('try again, BDF not found')
        ##now we have the vendor id
        if Monostate._inner.mlxDut: ##mellanox device
            temp = "set pci -s" + str(BDF) + "02"
            device_id = Monostate._inner.CliAgent.exec_command(temp) ##command: set pci -s BDF 02 (device id)
            flag = 1
            for device in device_cr_space.keys():
                if device == device_id:
                    flag = 0
                    if name_of_component == "dut":
                        if Monostate._inner.dutHasSecureFw:
                            Monostate._inner.dutComponent.CR_space.set_read_only_flag()
                        Monostate._inner.dutComponent.CR_space = CR_space_agent()
                    elif name_of_component == "upstreamComponent":
                        Monostate._inner.upstreamComponent.CR_space = CR_space_agent()
                    else:##name_of_component=="downstreamcomponent
                        Monostate._inner.downstreamComponent.CR_space = CR_space_agent()
            if flag:
                print("not found this device")
        else:
            if name_of_component == "dut":
                Monostate._inner.dutComponent.CR_space=None
            elif name_of_component == "upstreamComponent":
                Monostate._inner.upstreamComponent.CR_space = None
            else:  ##name_of_component=="downstreamcomponent
                Monostate._inner.downstreamComponent.CR_space = None



    def find_BDF_according_the_device(self,device_number):
        for num in device_name.keys():
            if num == device_number:
                name_of_device = device_name[num]
        if name_of_device == "BW":
            Monostate._inner.dutComponent.BDF = self.find_BW_BDF()
        elif name_of_device == "Connect_x_5":
            Monostate._inner.dutComponent.BDF = self.find_Connect_x_5_BDF()
        else:
            Monostate._inner.dutComponent.BDF = self.find_other_BDf()

    def find_BW_BDF(self):
        primery_bus = Monostate._inner.CliAgent.exec_command("mcra 0X11021c.8")  ##command:mcra 0X11021c.8
        bridge = 123 ####################ask
        function = "0"
        BDF=primery_bus+str(2*bridge)+function
        return BDF

    def find_Connect_x_5_BDF(self):
        primery_bus = Monostate._inner.CliAgent.exec_command("mcra 0X11021c.8") ####################ask
        bridge = "123" ####################ask
        function = "0"
        BDF=primery_bus+bridge+function
        return BDF

    def find_other_BDf(self):
        mst_output = Monostate._inner.CliAgent.exec_command("mst status") ####################ask
        cr_space_str = Monostate._inner.dut
        BDF=0
        for line in mst_output: ##mybee skip the first 7 line ? ?   ?ask
            if cr_space_str in line: ##we are in the line of the match cr space
                next(line)
                try: ####catch the BDF
                   BDF = re.search('fn=(.+?) addr', line).group(1)
                except AttributeError:
                    # fn=, addr not found in the original string
                    BDF = 'BDF not found'
                break
        return BDF

    def find_topology(self):
        #create a header type property
        heder_type_property=HeaderTypeProperty()
        heder_type=heder_type_property.get() #get the header type
        if heder_type:    ##header_type==1 ->dut is upstream
            Monostate._inner.dutIsUpstream = 1
            Monostate._inner.upstreamComponent = Monostate._inner.dutComponent
            self.find_dsc_component_BDF_conf_space() #find the other side of the link
            self.find_cr_space(Monostate._inner.upstreamComponent.BDF, "upstreamComponent")
        else:
            Monostate._inner.dutIsUpstream = 0
            Monostate._inner.downstreamComponent = Monostate._inner.dutComponent
            self.find_usc_component_BDF_conf_space() ###find the other side of the link
            self.find_cr_space(Monostate._inner.downstreamComponent.BDF, "downstreamComponent")



    def find_dsc_component_BDF_conf_space(self):
        temp = "set pci -s" + Monostate._inner.upstreamComponent.BDF + "19h"
        secondary_bus_number = Monostate._inner.CliAgent.exec_command(temp)
        Monostate._inner.downstreamComponent.BDF=secondary_bus_number ###ask !
        Monostate._inner.downstreamComponent.conf_space = conf_space_agent()

    def find_usc_component_BDF_conf_space(self):
        temp = "readlink - f / sys / bus / pci / devices /" + Monostate._inner.downstreamComponent.BDF + "19h"
        BDF=Monostate._inner.CliAgent.exec_command(temp)
        Monostate._inner.upstreamComponent.BDF = BDF  ###ask !
        Monostate._inner.upstreamComponent.conf_space = conf_space_agent()



























