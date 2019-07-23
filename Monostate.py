import re
import sys

sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project/Feature')
sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project/property')
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
    hex(4119): "/dev/mst/mt4119_pciconf0 ",
    hex(4117): "/dev/mst/mt4117_pciconf0",
    hex(1007): "/dev/mst/mt4103_pciconf0",
    hex(4117): "/dev/mst/mt4117_pciconf0",
    hex(41682): "/dev/mst/mt41682_pciconf0",
    hex(6517): "/dev/mst/mt41682_pciconf0"

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
            self._inner.CliAgent = CLiAgentRemote(serverName)
        else:
            self._inner.serverName = "Local"
            self._inner.CliAgent = CliAgentLocal()
        status, output = self._inner.CliAgent.execute_job_and_return_returncode_and_output("mst start")

    def init_MtUsb_input(self):
        self._inner.mlxDut = True
        self._inner.dutComponent.resources.set_CRspace_agent(
            crspace_agent(self._inner.dut))  #######what is the input for CR space agent
        if self._inner.dutPortNumber is None:
            print "the DUT is MtUsb , you must provide port number in the input"
            exit(1)
        if self._inner.dutPortNumber < 0:
            print "port number can not be less then 0 please try again"
        self._inner.dutComponent.resources.CR_space_agent.setPortNumber(self._inner.dutPortNumber)

    def init_BDF_Device_input(self):
        self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent(self._inner.dut))
        self.find_cr_space("dut")
        self.findPortNumber(self._inner.dutPortNumber, self._inner.dutComponent)
        # now we have all the information about the dut
        self.find_topology()

    def init_CRspace_Device_input(self):
        self._inner.mlxDut = True
        self._inner.dutComponent.resources.set_CRspace_agent(crspace_agent(self._inner.dut))
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
                        self._inner.dutComponent.resources.set_CRspace_agent(crspace_agent(cr_space_str))
                        self._inner.dutComponent.setIsSwitch(
                            self.checkIfSwitch(device_id, self._inner.dutComponent.resources.CR_space_agent))
                        if self.check_if_dutHasSecureFw():
                            self._inner.dutComponent.resources.CR_space_agent.set_read_only_flag()
                    elif name_of_component == "upstreamComponent":
                        self._inner.upstreamComponent.resources.set_CRspace_agent(crspace_agent(cr_space_str))
                        self._inner.dutComponent.setIsSwitch(
                            self.checkIfSwitch(device_id, self._inner.upstreamComponent.resources.CR_space_agent))
                    else:  ##name_of_component=="downstreamcomponent
                        self._inner.downstreamComponent.resources.set_CRspace_agent(crspace_agent(cr_space_str))
                        self._inner.dutComponent.setIsSwitch(
                            self.checkIfSwitch(device_id, self._inner.downstreamComponent.resources.CR_space_agent))

            if flag:
                print("not found this device")
        if not self._inner.mlxDut or flag:  # no mlx device
            if name_of_component == "dut":
                self._inner.dutComponent.resources.set_CRspace_agent(crspace_agent(None))
            elif name_of_component == "upstreamComponent":
                self._inner.upstreamComponent.resources.set_CRspace_agent(crspace_agent(None))
            else:  ##name_of_component=="downstreamcomponent
                self._inner.downstreamComponent.resources.set_CRspace_agent(crspace_agent(None))

    def checkIfSwitch(self, deviceId, resurceCrSpace):
        if str(deviceId) == hex(41682) or str(deviceId) == hex(6517):  # BF device
            return True
        if str(deviceId) == hex(4119) or str(deviceId) == hex(4121):  # galil device
            return resurceCrSpace.mst_read(resurceCrSpace.get_CRspace(), 0Xf8b0, 0, 1)
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

            else:
                mask = 0b0000000000000001
                rangeOfFor = 8
                if pcoreAdd == 0:
                    rangeOfFor = 16
                found = False
                for port in range(rangeOfFor):
                    if activeHost & mask != 0:
                        pciComponent.resources.CR_space_agent.setPortNumber(port+pcoreAdd)
                        if busOfTheComponent == (compliterId.get_with_CRspace() >> 8):
                            pciComponent.resources.CR_space_agent.setPortNumber(port+pcoreAdd)
                            found = True
                            break
                    mask = mask << 1
                #if pciComponent.resources.CR_space_agent.getPortNumber() is None:
                    if not found:
                        print "cant find port number , probabely BDF wrong "
                        exit(1)
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
            self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent(self.find_BW_BDF()))
            return
        elif name_of_device == "galil" and self._inner.dutComponent.resources.get_CRspace_agent().mst_read('pcie_switch_en'):
            self._inner.dutComponent.setIsSwitch(True)
            self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent(self.find_galil_switch_BDF()))
            return
        else:
            self._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent(self.find_other_BDf()))

    def find_BW_BDF(self):
        if not(self._inner.dutPortNumber >=20 or self._inner.dutPortNumber <=27 and
            self._inner.dutPortNumber >= 30 or self._inner.dutPortNumber <= 37):
            print "invalid port number"
            exit(1)
        compliterId = CompliterIdProperty.CompliterIdProperty(self._inner.dutComponent.resources)
        self._inner.dutComponent.resources.CR_space_agent.setPortNumber(int(self._inner.dutPortNumber))
        compliterIdReturn = compliterId.get_with_CRspace()
        B = int(compliterIdReturn >> 8)
        D = int(compliterIdReturn & 0x00ff)
        F = 0
        return bdf_feature.bdf_feature(B, D, F).bdf



    def find_galil_switch_BDF(self):
        activeHost = ActiveHostProperty.ActiveHostProperty(self._inner.dutComponent.resources).get_with_CRspace()
        compliterId = CompliterIdProperty.CompliterIdProperty(self._inner.dutComponent.resources)
        counter = 0
        mask = 0b0000000000000001
        found = False
        for port in range(16):
            if activeHost & mask != 0:
                counter += 1
                if counter == int(self._inner.dutPortNumber)+1:
                    self._inner.dutComponent.resources.CR_space_agent.setPortNumber(int(port))
                    compliterIdReturn = compliterId.get_with_CRspace()
                    B = int(compliterIdReturn >> 8)
                    D = int(compliterIdReturn & 0x00ff)
                    F=0
                    found = True
                    return bdf_feature.bdf_feature(B, D, F).bdf
            mask = mask << 1
            if not found:
                print "inactive port number inserted"
                exit(1)

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
                self._inner.downstreamComponent.resources.set_Confspace_agent(conf_space_agent(bdf))
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
                self._inner.upstreamComponent.resources.set_Confspace_agent(conf_space_agent(bdf))
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


# -----------------------------------------------------------------------
# CR space agent, here until we find solution for the import problem
# -----------------------------------------------------------------------
class crspace_agent:

    def __init__(self, CRspace):
        self.Crspace = CRspace  # str
        self.portNumber = None
        self.read_only = False

    def get_CRspace(self):
        return self.Crspace

    def set_read_only_flag(self):
        self.read_only = True

    def setPortNumber(self, portNum):
        self.portNumber = portNum

    def getPortNumber(self):
        return self.portNumber

    def mst_read(self, device, address, offset=0, size=32):
        """ perform mst_read for given device, address, offset and size
        :param device - expected /dev/mst/mtxxxx_pciconf0 or other that will suite OS type
        :param address - taken from crspace_db
        :param offset - taken from crspace_db
        :param size  - taken from crspace_db
        :return : value for mcra /dev/mst/mtxxxxxxxx 0x<address>.offset:size
        rtype str in hex
        """
        server = Monostate()
        cmd = "mcra " + device + " " + str(hex(address)) + "." + str(offset) + ":" + str(size)
        (status, output) = server._inner.CliAgent.execute_job_and_return_returncode_and_output(cmd)
        if status:
            return None
        output = eval(output)
        # after_analysis = operator.rshift(output, offset) & (operator.lshift(1, size) - 1)
        print("mcra read: {} - result is: {} ".format(cmd, hex(output)))
        return output

    def mst_write(self, device, address, value, offset=0, size=32):
        """ perform mst_read for given device, address, offset and size
        :param device - expected /dev/mst/mtxxxx_pciconf0 or other that will suite OS type
        :param value_to_write - what to write to register
        :param address - taken from crspace_db
        :param offset - taken from crspace_db
        :param size  - taken from crspace_db
        :return : value for mcra /dev/mst/mtxxxxxxxx 0x<address>.offset:size
        rtype str in hex
        """
        server = Monostate()
        # word = self.mst_read(device, address)
        # mask = operator.lshift((operator.lshift(1, size) - 1), offset)
        # word = (word & ~mask | ((operator.lshift(value, offset) & mask)))
        cmd = "mcra " + device + " " + str(hex(address)) + "." + str(offset) + ":" + str(size) + " " + str(hex(value))
        (status, output) = server._inner.CliAgent.execute_job_and_return_returncode_and_output(cmd)
        print("mcra write: {} - return status is: {} ".format(cmd, status))
        if status != 0:
            return -1
        return 0

    def return_register(self, register_to_return):
        inf_singletone = Monostate()
        try:
            return_value = inf_singletone.crspace_device.REGISTERS[register_to_return]
        except KeyError:
            print "register_to_return : " + register_to_return + " Not found in device crspace map"
            exit(1)

    ############################################################

    ADDRESS = 0
    OFFSET = 1
    SIZE = 2
    DEFAULT_VALUE = 3
    SPACES_FOT_NEXT_ELEMENT = 4
    NUMBER_OF_AVAILABLE_NEXT_ELEMENTS = 5

    def get_pcie_data(self, field_name):
        inf_singletone = Monostate()
        addr = inf_singletone.crspace_agent.return_register(field_name)
        output = self.mst_read(inf_singletone.variables.args.mstdev, addr[self.ADDRESS], addr[self.OFFSET],
                               addr[self.SIZE])
        return output

    def set_pcie_data(self, field_name, new_val, use_default_value=0, show_value_of_register_after_write=0,
                      multiple_prints=0):
        inf_singletone = Monostate()
        addr = inf_singletone.crspace_agent.return_register(field_name)
        if (use_default_value == 1):
            new_val = addr[self.DEFAULT_VALUE]
        gaps_between_registers = 0
        num_of_rep = 1
        if (multiple_prints == 1):
            gaps_between_registers = addr[self.SPACES_FOT_NEXT_ELEMENT]
            num_of_rep = int(addr[self.NUMBER_OF_AVAILABLE_NEXT_ELEMENTS])
        for x in range(0, num_of_rep):
            address_with_gap = addr[self.ADDRESS] + gaps_between_registers * x
            output = self.mst_write(inf_singletone.variables.args.mstdev, address_with_gap, new_val, addr[self.OFFSET],
                                    addr[self.SIZE])
            # print("{},{},{}".format(hex(address_with_gap),addr[1],addr[2]))
            if (show_value_of_register_after_write == 1):
                print("read after write: {}".format(hex(
                    self.mst_read(inf_singletone.variables.args.mstdev, address_with_gap, addr[self.OFFSET],
                                  addr[self.SIZE]))))

        return output


# -------------------------------------------------------------------------
# conf space agent, here until we find solution for the import problem
# -------------------------------------------------------------------------


class conf_space_agent:
    FIRST_N_CAP_PTR = 0x34
    FIRST_E_CAP_PTR = 0x100

    def __init__(self, bdf):
        self.cap_address_n = {}
        self.cap_address_e = {}
        self._bdf = bdf
        self._server = Monostate()
        self.init_capbilities_table()
        # self.print_capalities()

    def get_bdf(self):
        return self._bdf

    def set_bdf(self, BDF):
        self._bdf = BDF

    def exe_cmd(self, cmd, print_cmd=False):
        (status, val) = self._server._inner.CliAgent.execute_job_and_return_returncode_and_output(cmd,
                                                                                                  print_cmd=print_cmd)
        return status, val

    def init_capbilities_table(self):
        ## Normal Configuration space
        self.cap_address_n[0] = 0  # PCI_HEADER_NORMAL
        cmd = "setpci -s " + self._bdf + " " + str(hex(self.FIRST_N_CAP_PTR)) + ".w"
        (status, val) = self.exe_cmd(cmd, False)
        nextPtr = int(val, 16)
        while (nextPtr != 0):
            cmd = "setpci -s " + self._bdf + " " + str(hex(nextPtr)) + ".w"
            (status, val) = self.exe_cmd(cmd, False)
            foundId = int(val, 16) & 0xff
            self.cap_address_n[foundId] = nextPtr
            nextPtr = int(val, 16) >> 8

        ## Extended Configuration space
        nextPtr = self.FIRST_E_CAP_PTR
        while (nextPtr != 0):
            cmd = "setpci -s " + self._bdf + " " + str(hex(nextPtr)) + ".l"
            (status, val) = self.exe_cmd(cmd)
            foundId = int(val, 16) & 0xffff
            self.cap_address_e[foundId] = nextPtr
            nextPtr = int(val, 16) >> 20

    def read_bits_from_reg(self, regVal, bitLoc, size):
        mask = (1 << size) - 1
        return (regVal >> bitLoc) & mask;

    def read_capbilities(self, capID, isExtended, offset, bit_loc, size):
        reg_offset = (self.cap_address_e[capID] if isExtended else self.cap_address_n[capID]) + offset
        aligned_offset = reg_offset & 0xffffffc  # get to the near by long word address
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, val) = self.exe_cmd(cmd, print_cmd=False)
        val = (int(val, 16) >> ((reg_offset % 4) * 8))
        bitsVal = self.read_bits_from_reg(val, bit_loc, size)
        return hex(bitsVal)

    def read_header(self, offset, bit_loc, size):
        aligned_offset = offset & 0xffffffc  # get to the near by long word address
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, val) = self.exe_cmd(cmd, print_cmd=False)
        val = (int(val, 16) >> ((offset % 4) * 8))
        bitsVal = self.read_bits_from_reg(val, bit_loc, size)
        return hex(bitsVal)

    def write(self, capID, isExtended, offset, bit_loc, size, value):
        reg_offset = (self.cap_address_e[capID] if isExtended else self.cap_address_n[capID]) + offset
        aligned_offset = reg_offset & 0xffffffc  # get to the near by long word address
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, org_val) = self.exe_cmd(cmd, print_cmd=False)
        bit_loc_aligned = bit_loc + ((reg_offset % 4) * 8)
        reset_mask = ((1 << size) - 1) << bit_loc_aligned
        new_val = (int(org_val, 16) & ~reset_mask) | (value << bit_loc_aligned)
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l=" + str(hex(new_val))
        status = self.exe_cmd(cmd, print_cmd=False)
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, read_val) = self.exe_cmd(cmd, print_cmd=False)
        return read_val

    def print_capalities(self):
        print ('{:*^30}').format("  BDF : " + self._bdf + "  ")
        print ('{: ^8}'.format("CapID") + " | " + '{: ^8}'.format("offset") + " | " + '{: ^8}'.format("Extended"))
        print ('{:-^30}').format("")
        for k in sorted(self.cap_address_n.keys()):
            print ('{: ^8}'.format(hex(k)) + " | " +
                   '{: ^8}'.format(hex(self.cap_address_n[k])) + " | " +
                   '{: ^8}'.format("No"))
        for k in sorted(self.cap_address_e.keys()):
            print ('{: ^8}'.format(hex(k)) + " | " +
                   '{: ^8}'.format(hex(self.cap_address_e[k])) + " | " +
                   '{: ^8}'.format("Yes"))


# def speed_change_example(DSConf , USConf , speed):
#     DSConf.print_capalities()
#     link_speed  = hex(DSConf.read(0x10, False, 0x12, 0, 4))
#     print "current Link speed" , link_speed
#     print "Changing target link speed to Gen"+speed
#     link_target_updated = USConf.write(0x10, False, 0x30, 0, 4, int(speed))
#     print "Executing disable enable flow"
#     USConf.write(capID=0x10, isExtended=False, offset=0x10, bit_loc=4, size=1, value=1)
#     time.sleep(50e-3)
#     USConf.write(0x10, False, 0x10, 4, 1, 0)
#     time.sleep(1)
#     link_speed = hex(DSConf.read(0x10, False, 0x12, 0, 4))
#     print "current Link speed", link_speed , ("PASSED" if int(speed) == int(link_speed, 16) else "FAILED")


# -------------------------------------------------------------------------
# CLI agent, here until we find solution for the import problem
# -------------------------------------------------------------------------
class CliAgentLocal:
    serverName = None

    def __init__(self, ostype='Linux'):
        self.osType = ostype
        self.serverName = "Local"

    def execute_job_and_return_returncode_and_output(self, command, print_cmd=False):
        """ preform cli command on server your running python from .
        :param basestring command: the cli command
        :param boolean print_cmd: the output should be printed to stdout
        :return : process
        rtype int
        """

        output = []
        RC = 0
        if print_cmd:
            print("command is: {}".format(command))
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as exp:  ##If subprocess return code is non-zero
            RC = exp.returncode
        return RC, output

    def execute_job_in_bg_without_returning_output(self, command):
        """ preform cli command on server your running python from .
        :param command: the cli command to execute
        :return : non
        rtype int
        """

        output = []
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, close_fds=True)
        return proc

    # def exec_command(self, command, print_cmd=False):
    #     if print_cmd:
    #         print("executing command:" + command)
    #     try:
    #         proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
    #                                 stdout=subprocess.PIPE,
    #                                 stderr=subprocess.STDOUT, close_fds=True)
    #         proc.wait()
    #     except subprocess.CalledProcessError as e:
    #         print "Failed to run command"
    #         return e.returncode
    #
    #     stdout, stderr = proc.communicate()
    #     return stdout, stderr
    #
    # def exec_command_bg(self, command, print_cmd=False):
    #     if print_cmd:
    #         print("executing command:" + command)
    #     proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
    #                             stdout=subprocess.PIPE,
    #                             stderr=subprocess.STDOUT, close_fds=True)
    #     return proc
    #
    # def kill_proc(self):
    #     pass


class CLiAgentRemote:
    serverName = None
    client = None

    def __init__(self, serverName, ostype):
        self.osType = ostype
        self.serverName = serverName

    def connect_to_remote_server(self):
        client = paramiko.SSHClient()
        try:
            client.connect(self.serverName, username="root", password="3tango")
        except paramiko.ssh_exception.AuthenticationException:
            print "Failed to connect to remote server"
            return 1
        self.client = client

    def execute_job_and_return_returncode_and_output(self, command, print_cmd=False):
        if print_cmd:
            print("executing command:" + command)
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
        except paramiko.ssh_exception.SSHException:
            print "Failed to execute the command"
            return 1
        return stdout.channel.recv_exit_status(), stdout
