import re
import sys
sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project')
sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project/Feature')
sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project/property')
import Agents.cli_agent as cli
import Agents.crspace_agent as crspace_agent
import Agents.conf_space_agent as conf_space_agent
import PciComponent
import HeaderTypeProperty
import VendorIDProperty
import ActiveHostProperty
import CompliterIdProperty

import datetime
import time
import subprocess
import paramiko
import bdf_feature
import PrimaryBusProperty

#######################data ####################
device_cr_space = {  ##key =device ID , value= CR_space_name
    hex(4119): "/dev/mst/mt4119_pciconf0",
    hex(4117): "/dev/mst/mt4117_pciconf0",
    hex(1007): "/dev/mst/mt4103_pciconf0",
    hex(4117): "/dev/mst/mt4117_pciconf0",
    hex(41682): "/dev/mst/mt41682_pciconf0",
    hex(6517): "/dev/mst/mt41682_pciconf0",
    hex(4121): "/dev/mst/mt4121_pciconf0"

}

device_name = {  ##key =device ID , value= CR_space_name
    "/dev/mst/mt4119_pciconf0": "galil",
    "/dev/mst/mt4117_pciconf0": "dotan",
    "/dev/mst/mt4103_pciconf0": "Connect_x_3_pro",
    '/dev/mst/mt4115_pciconf0': 'shomron',
    '/dev/mst/mt41682_pciconf0': 'BW',
    "/dev/mst/mt4121_pciconf0": "galil",
    '/dev/mst/mt4113_pciconf0': 'negev',

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
            self.dutComponent = None  # pci component
            self.rootPortComponent = None
            self.upstreamComponent = None  # pci component
            self.downstreamComponent = None  # pci component
            self.CliAgent = None
            self.dutPortNumber = None

    def __init__(self, dut="", serverName="Local", portNumber=None):
        if Monostate._inner is None:
            Monostate._inner = Monostate.inner()
            self._inner.dut = dut
            self._inner.dutPortNumber = portNumber
            self.evalDutType()
            self.evalServerName(serverName)
            self._inner.dutComponent = PciComponent.PciComponent()
            self._inner.upstreamComponent = PciComponent.PciComponent('USC')
            self._inner.downstreamComponent = PciComponent.PciComponent('DSC')
            if self._inner.dutType == "BDF Device":
                self.init_BDF_Device_input()
            elif self._inner.dutType == "CRspace Device":
                self.init_CRspace_Device_input()
            elif self._inner.dutType == "MTusb Device":
                self.init_MtUsb_input()
            elif self._inner.dutType == "Unknown Device":
                print "Unknown Device cant continue"
                exit(1)
            print("Monostate done")

    def evalDutType(self):
        if ":" in self._inner.dut:
            self._inner.dutType = "BDF Device"
        elif "mst" in self._inner.dut:
            self._inner.dutType = "CRspace Device"
        elif "MTusb" in self._inner.dut:
            self._inner.dutType = "MTusb Device"
        else:
            self._inner.dutType = "Unknown Device"

    def evalServerName(self, serverName):
        if serverName is not "Local":
            self._inner.serverName = "Remote"
            self._inner.CliAgent = cli.CLiAgentRemote(serverName)
        else:
            self._inner.serverName = "Local"
            self._inner.CliAgent = cli.CliAgentLocal()
        status, output = self._inner.CliAgent.execute_job_and_return_returncode_and_output("mst start")

    def init_MtUsb_input(self):
        self._inner.mlxDut = True
        self._inner.dutComponent.resources.set_CRspace_agent(
            crspace_agent.crspace_agent(self._inner.dut, self._inner.CliAgent))  #######what is the input for CR space agent
        if self._inner.dutPortNumber is None:
            print "the DUT is MtUsb , you must provide port number in the input"
            exit(1)
        if self._inner.dutPortNumber < 0:
            print "port number can not be less then 0 please try again"
        self._inner.dutComponent.resources.CR_space_agent.setPortNumber(self._inner.dutPortNumber)

    def init_BDF_Device_input(self):
        self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent.conf_space_agent(self._inner.dut, self._inner.CliAgent))
        self.find_cr_space("dut")
        isDutDevice=True
        self.findPortNumber(self._inner.dutPortNumber, self._inner.dutComponent,isDutDevice)
        # now we have all the information about the dut
        self.find_topology()

    def init_CRspace_Device_input(self):
        self._inner.mlxDut = True
        self._inner.dutComponent.resources.set_CRspace_agent(crspace_agent.crspace_agent(self._inner.dut, self._inner.CliAgent))
        self.find_BDF_according_the_device(self._inner.dut)
        ##the device_number
        # now we have all the information about the dut
        isDutDevice=True
        self.findPortNumber(self._inner.dutPortNumber, self._inner.dutComponent,isDutDevice)
        self.find_topology()

    def find_cr_space(self, name_of_component):
        if name_of_component == "dut":
            vendor_id_pro = VendorIDProperty.VendorIDProperty(self._inner.dutComponent.resources)
        elif name_of_component == "upstreamComponent":
            vendor_id_pro = VendorIDProperty.VendorIDProperty(self._inner.upstreamComponent.resources)
        else:  ##name_of_component=="downstreamcomponent
            vendor_id_pro = VendorIDProperty.VendorIDProperty(self._inner.downstreamComponent.resources)
        vendor_ID = vendor_id_pro.get_with_Confspace()
        ##now we have the vendor id
        self._inner.mlxDut = vendor_id_pro.is_mlx_device()
        flag = True
        if self._inner.mlxDut:  ##mellanox device
            if name_of_component == 'dut':
                device_id = self._inner.dutComponent.resources.conf_space_agent.read_header(0x02, 0, 16)
            elif name_of_component == 'upstreamComponent':
                device_id = self._inner.upstreamComponent.resources.conf_space_agent.read_header(0x02, 0, 16)
            else:
                device_id = self._inner.downstreamComponent.resources.conf_space_agent.read_header(0x02, 0, 16)
            print device_id
            for device in device_cr_space.keys():
                if device == str(device_id):
                    flag = False
                    cr_space_str = device_cr_space[device]
                    if name_of_component == "dut":
                        self._inner.dutComponent.resources.set_CRspace_agent(crspace_agent.crspace_agent(cr_space_str, self._inner.CliAgent))
                        self._inner.dutComponent.setIsSwitch(
                            self.checkIfSwitch(device_id, self._inner.dutComponent.resources.CR_space_agent))
                        if self.check_if_dutHasSecureFw():
                            self._inner.dutComponent.resources.CR_space_agent.set_read_only_flag()
                    elif name_of_component == "upstreamComponent":
                        self._inner.upstreamComponent.resources.set_CRspace_agent(crspace_agent.crspace_agent(cr_space_str, self._inner.CliAgent))
                        self._inner.dutComponent.setIsSwitch(
                            self.checkIfSwitch(device_id, self._inner.upstreamComponent.resources.CR_space_agent))
                    else:  ##name_of_component=="downstreamcomponent
                        self._inner.downstreamComponent.resources.set_CRspace_agent(crspace_agent.crspace_agent(cr_space_str, self._inner.CliAgent))
                        self._inner.dutComponent.setIsSwitch(
                            self.checkIfSwitch(device_id, self._inner.downstreamComponent.resources.CR_space_agent))

            if flag:
                print("not found this device")
        if not self._inner.mlxDut or flag:  # no mlx device
            if name_of_component == "dut":
                self._inner.dutComponent.resources.set_CRspace_agent(crspace_agent.crspace_agent(None, self._inner.CliAgent))
            elif name_of_component == "upstreamComponent":
                self._inner.upstreamComponent.resources.set_CRspace_agent(crspace_agent.crspace_agent(None, self._inner.CliAgent))
            else:  ##name_of_component=="downstreamcomponent
                self._inner.downstreamComponent.resources.set_CRspace_agent(crspace_agent.crspace_agent(None, self._inner.CliAgent))

    def checkIfSwitch(self, deviceId, resurceCrSpace):
        if str(deviceId) == hex(41682) or str(deviceId) == hex(6517):  # BF device
            return True
        if str(deviceId) == hex(4119) or str(deviceId) == hex(4121):  # galil device
            return resurceCrSpace.mst_read("pcie_switch_en")
        else:  # the device cant be a switch
            return False

    def findPortNumber(self, portNumber, pciComponent, isDutDevice):
        componentCrSpace = pciComponent.resources.CR_space_agent.get_CRspace()
        if componentCrSpace is None:
            pciComponent.resources.CR_space_agent.setPortNumber('None')
            return
        if pciComponent.getIsSwitch() and isDutDevice:
            if portNumber is None:
                print "the device is switch , you must provide port number in the input"
                exit(1)
            if self._inner.dutPortNumber < 0:
                print "port number can not be less then 0 please try again"
                exit(1)
            pciComponent.resources.CR_space_agent.setPortNumber(self._inner.dutPortNumber)
            activeHost = ActiveHostProperty.ActiveHostProperty(pciComponent.resources).get_with_CRspace()
            valid = self.check_if_port_valid(device_name[componentCrSpace],activeHost)
            if not valid:
                print "Port number isn't valid"
                exit(1)
            return
        else:
            busOfTheComponent = bdf_feature.bdf_feature(bdf=pciComponent.resources.conf_space_agent.get_bdf()).bus
            pcoreAdd=0
            if device_name[componentCrSpace] == 'negev' or device_name[componentCrSpace] == 'BW':
                PrimaryBusPro = PrimaryBusProperty. PrimaryBusProperty(pciComponent.resources)
                #deviceOfTheComponent = bdf_feature.bdf_feature(bdf=pciComponent.resources.conf_space_agent.get_bdf()).device
                pciComponent.resources.CR_space_agent.setPortNumber(20)
                pcoreAdd=20
                if busOfTheComponent != PrimaryBusPro.get_with_CRspace():
                    pciComponent.resources.CR_space_agent.setPortNumber(30)
                    pcoreAdd=30
            activeHost = ActiveHostProperty.ActiveHostProperty(pciComponent.resources).get_with_CRspace()
            compliterId = CompliterIdProperty.CompliterIdProperty(pciComponent.resources)
            if device_name[componentCrSpace] == 'shomron' or device_name[componentCrSpace] == 'dotan':
                found = False
                for port in range(activeHost):
                    pciComponent.resources.CR_space_agent.setPortNumber(port)
                    if busOfTheComponent == (compliterId.get_with_CRspace() >> 8):
                        pciComponent.resources.CR_space_agent.setPortNumber(port)
                        found = True
                        break
                #if pciComponent.resources.CR_space_agent.getPortNumber() is None:
                    if not found:
                        print "cant find port number , probabely BDF wrong "
                        exit(1)
            #         #########################################################

            elif device_name[componentCrSpace] == 'negev' or device_name[componentCrSpace] == 'BW':
                deviceOfTheComponent = bdf_feature.bdf_feature(bdf=pciComponent.resources.conf_space_agent.get_bdf()).device
                width = self.count_1_in_reg(activeHost, 16)
                pciComponent.resources.CR_space_agent.setPortNumber(deviceOfTheComponent/width+pcoreAdd)
            elif device_name[componentCrSpace] == 'galil':
                deviceOfTheComponent = bdf_feature.bdf_feature(bdf=pciComponent.resources.conf_space_agent.get_bdf()).device
                pciComponent.resources.CR_space_agent.setPortNumber(deviceOfTheComponent)
#                 mask = 0b0000000000000001
#                 rangeOfFor = 8
#                 if pcoreAdd == 0:
#                     rangeOfFor = 16
#                 found = False
#                 print activeHost
#                 print pcoreAdd
#                 for port in range(rangeOfFor):
#                     if activeHost & mask != 0:
#                         pciComponent.resources.CR_space_agent.setPortNumber(port+pcoreAdd)
#                         if busOfTheComponent == (compliterId.get_with_CRspace() >> 8):
#                             pciComponent.resources.CR_space_agent.setPortNumber(port+pcoreAdd)
#                             found = True
#                             break
#                     mask = mask << 2
#                 #if pciComponent.resources.CR_space_agent.getPortNumber() is None:
#                 if not found:
#                     print "cant find port number , probabely BDF wrong "
#                     exit(1)
        print "port :::::::" + str(pciComponent.resources.CR_space_agent.getPortNumber()) #debug

    def check_if_dutHasSecureFw(self):
        cr_space = self._inner.dutComponent.resources.CR_space_agent.get_CRspace()
        temp = "flint -d" + str(cr_space) + "q"
        status, output = self._inner.CliAgent.execute_job_and_return_returncode_and_output(temp)
        for line in output:
            if "Security Attributes" in line:
                data = line.split(":")
                is_secure = data[1].strip()
                if 'N/A' == is_secure:
                    self._inner.dutHasSecureFw = False
                    return False
        self._inner.dutHasSecureFw = True
        return True

    def find_BDF_according_the_device(self, device_number):
        name_of_device = ""
        for num in device_name.keys():
            if num == device_number:
                name_of_device = device_name[num]
                break
        if name_of_device == "BW":
            self._inner.dutComponent.setIsSwitch(True)
            self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent.conf_space_agent(self.find_BW_BDF(), self._inner.CliAgent))
            return
        elif name_of_device == "galil" and self._inner.dutComponent.resources.get_CRspace_agent().mst_read('pcie_switch_en'):
            self._inner.dutComponent.setIsSwitch(True)
            self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent.conf_space_agent(self.find_galil_switch_BDF(), self._inner.CliAgent))
            return
        else:
            self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent.conf_space_agent(self.find_other_BDf(), self._inner.CliAgent))

    def find_BW_BDF(self):
        primarybusprop = PrimaryBusProperty.PrimaryBusProperty(self._inner.dutComponent.resources)
        self._inner.dutComponent.resources.CR_space_agent.setPortNumber(int(self._inner.dutPortNumber))
        primaryBus = primarybusprop.get_with_CRspace()
        activeHost = ActiveHostProperty.ActiveHostProperty(self._inner.dutComponent.resources).get_with_CRspace()
        width = 16/self.count_1_in_reg(activeHost, 16)
        mod = int(self._inner.dutPortNumber/10)*10
        port = self._inner.dutPortNumber%mod
        B = int(primaryBus)
        D = port*width
        F = 0
        
#         compliterId = CompliterIdProperty.CompliterIdProperty(self._inner.dutComponent.resources)
#         self._inner.dutComponent.resources.CR_space_agent.setPortNumber(int(self._inner.dutPortNumber))
#         compliterIdReturn = compliterId.get_with_CRspace()
#         B = int(compliterIdReturn >> 8)
#         D = int(compliterIdReturn & 0x00ff)
#         F = 0
        return bdf_feature.bdf_feature(B, D, F).bdf



    def find_galil_switch_BDF(self):
        primarybusprop = PrimaryBusProperty.PrimaryBusProperty(self._inner.dutComponent.resources)
        self._inner.dutComponent.resources.CR_space_agent.setPortNumber(int(self._inner.dutPortNumber))
        primaryBus = primarybusprop.get_with_CRspace()
        activeHost = ActiveHostProperty.ActiveHostProperty(self._inner.dutComponent.resources).get_with_CRspace()
        width = 16/self.count_1_in_reg(activeHost, 16)
        port = self._inner.dutPortNumber
        B = int(primaryBus)
        D = port*width
        F = 0
        return bdf_feature.bdf_feature(B, D, F).bdf
#         activeHost = ActiveHostProperty.ActiveHostProperty(self._inner.dutComponent.resources).get_with_CRspace()
#         compliterId = CompliterIdProperty.CompliterIdProperty(self._inner.dutComponent.resources)
#         counter = 0
#         mask = 0b0000000000000001
#         found = False
#         for port in range(16):
#             if activeHost & mask != 0:
#                 counter += 1
#                 if counter == int(self._inner.dutPortNumber)+1:
#                     self._inner.dutComponent.resources.CR_space_agent.setPortNumber(int(port))
#                     compliterIdReturn = compliterId.get_with_CRspace()
#                     B = int(compliterIdReturn >> 8)
#                     D = int(compliterIdReturn & 0x00ff)
#                     F=0
#                     found = True
#                     return bdf_feature.bdf_feature(B, D, F).bdf
#             mask = mask << 1
#             if not found:
#                 print "inactive port number inserted"
#                 exit(1)

    def find_other_BDf(self):
        status, mst_output = self._inner.CliAgent.execute_job_and_return_returncode_and_output(
            "mst status")  ####################ask
        cr_space_str = self._inner.dut
        BDF = 0
        flag = False
        # print mst_output
        temp_list = mst_output.split('\n')
        for line in temp_list:  ##mybee skip the first 7 line ? ?   ?ask
            if cr_space_str in line:  ##we are in the line of the match cr space
                flag = True
                continue
            if flag:
                try:  ####catch the BDF
                    BDF = re.search('fn=0000:(.+?) addr', line).group(1)
                except AttributeError:
                    # fn=, addr not found in the original string
                    BDF = 'BDF not found'
                break
        return BDF

    def find_topology(self):
        heder_type_property = HeaderTypeProperty.HeaderTypeProperty(self._inner.dutComponent.resources)
        heder_type = heder_type_property.get_with_Confspace()  # get the header type
        print heder_type
        isDutDevice = False
        if heder_type == hex(0X1):  ##header_type==1 ->dut is upstream
            self._inner.dutIsUpstream = True
            self._inner.upstreamComponent = self._inner.dutComponent
            self.find_dsc_component_BDF_conf_space()  # find the other side of the link
            self.find_cr_space("downstreamComponent")
            self.findPortNumber(self._inner.dutPortNumber, self._inner.downstreamComponent, isDutDevice)
            print self._inner.downstreamComponent.resources.get_CRspace_agent().get_CRspace()
            print self._inner.downstreamComponent.resources.get_Confspace_agent().get_bdf()
        else:
            self._inner.dutIsUpstream = False
            self._inner.downstreamComponent = self._inner.dutComponent
            self.find_usc_component_BDF_conf_space()  ###find the other side of the link
            self.find_cr_space("upstreamComponent")
            self.findPortNumber(self._inner.dutPortNumber, self._inner.upstreamComponent,isDutDevice)
            print self._inner.upstreamComponent.resources.get_CRspace_agent().get_CRspace()
            print self._inner.upstreamComponent.resources.get_Confspace_agent().get_bdf()

    def find_dsc_component_BDF_conf_space(self):
        secondary_bus_number = self._inner.upstreamComponent.resources.conf_space_agent.read_header(0x19, 0, 8)
        if secondary_bus_number >= 0 and secondary_bus_number >= 9:
            secondary_bus_number = str(secondary_bus_number)
            secondary_bus_number = secondary_bus_number.strip("0x")
            secondary_bus_number = "0" + secondary_bus_number

        else:
            secondary_bus_number = str(secondary_bus_number)
            secondary_bus_number = secondary_bus_number.strip("0x")
        print secondary_bus_number
        bdf_list = self.read_current_bdfs_in_system()
        for bdf in bdf_list:
            if secondary_bus_number in bdf:
                self._inner.downstreamComponent.resources.set_Confspace_agent(conf_space_agent.conf_space_agent(bdf, self._inner.CliAgent))
                return
        print "cant find dsc, exiting.."
        exit(1)

    def find_usc_component_BDF_conf_space(self):
        downstream_BDF = self._inner.downstreamComponent.resources.conf_space_agent.get_bdf()
        bdf_f = bdf_feature.bdf_feature(bdf=downstream_BDF)
        bus = bdf_f.bus
        if bus >= 0 and bus <= 9:
            bus = "0" + str(bus)
        bdf_list = self.read_current_bdfs_in_system()
        for bdf in bdf_list:
            cmd = "lspci -s {} -vvv | grep -i secondary={} ".format(bdf, bus)
            rc, output = self._inner.CliAgent.execute_job_and_return_returncode_and_output(cmd)
            if not rc:
                self._inner.upstreamComponent.resources.set_Confspace_agent(conf_space_agent.conf_space_agent(bdf, self._inner.CliAgent))
                print "usc bdf: " + bdf
                return
        print "cant find usc, exiting.."
        exit(1)

    def read_current_bdfs_in_system(self):
        bdf_list = list()
        cmd = "lspci"
        rc, output = self._inner.CliAgent.execute_job_and_return_returncode_and_output(cmd)
        if rc is not 0:
            print "lspci failed, exiting.."
            exit(1)
        output = output.split('\n')
        for line in output:
            tmp = line.split()
            if not tmp:
                continue
            bdf_list.append(tmp[0])
        return bdf_list
    
    def count_1_in_reg(self, reg, sizeinbits):
        mask = 0b1
        counter = 0
        for bit in range(sizeinbits):
            if reg & mask != 0:
                counter+=1
            mask<<1
        return counter
    
    def check_if_port_valid(self,devicename, activehost):
        port_state = self._inner.dutComponent.resources.CR_space_agent.mst_read("port_state")
        width = 16/self.count_1_in_reg(activehost, 16)
        if devicename == "BW" or devicename == "negev":
            mod = int(self._inner.dutPortNumber/10)*10
            port = (self._inner.dutPortNumber%mod)*width
            if port%width == 0:
                if port_state == 0x70:
                    return True
            return False
            
        if devicename == "galil":
            port = self._inner.dutPortNumber
            if port%width == 0:
                if port_state == 0x70:
                    return True
            return False

    def getUscComponent(self):
        return self._inner.upstreamComponent

    def getDscComponent(self):
        return self._inner.downstreamComponent

