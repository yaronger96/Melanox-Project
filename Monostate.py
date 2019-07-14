import re
from PciComponent import PciComponent
from HeaderTypeProperty import HeaderTypeProperty
from VendorIDProperty import VendorIDProperty
import sys
import datetime
import time
import subprocess
import paramiko

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
            self.CliAgent = None

    def __init__(self,dut="",serverName = "Local"):
        if Monostate._inner is None:
            Monostate._inner = Monostate.inner()
         ##   monostate._inner.dut = dut
            self.dut = dut
            Monostate.evalDutType()
            Monostate.evalServerName( serverName )
            self.dutComponent = PciComponent()
            self.upstreamComponent = PciComponent()
            self.downstreamComponent = PciComponent()
            if(self.dutType == "BDF Device"):
                self.init_BDF_Device_input()
            elif (self.dutType == "CRspace Device"):
                self.init_CRspace_Device_input()
            elif (self.dutType == "MTusb Device"):
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
            Monostate._inner.CliAgent = CLiAgentRemote(serverName)
        else:
            Monostate._inner.serverName = "Local"
            Monostate._inner.CliAgent = CliAgentLocal()

    def init_MtUsb_input(self):
        Monostate._inner.mlxDut = True
        Monostate._inner.dutComponent.resources.set_CRspace_agent(crspace_agent()) #######what is the input for CR space agent

    def init_BDF_Device_input(self):
        Monostate._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent())
        # Monostate._inner.dutComponent.resources.conf_space.init_capbilities_table()
        Monostate._inner.dutComponent.dutComponent.resources.conf_space_agent.setBdf(self.dut)
        self.find_cr_space(self.dut, "dut")  #self.dut = BDF
        # now we have all the information about the dut
        self.find_topology()

    def init_CRspace_Device_input(self):
        Monostate._inner.mlxDut = True
        Monostate._inner.dutComponent.resources.set_CRspace_agent(crspace_agent(self.dut))
        input = Monostate._inner.dut.split("/")
        Monostate._inner.dutComponent.resources.set_Confspace_agent(conf_space_agent())
        #Monostate._inner.dutComponent.resources.conf_space.init_capbilities_table()
        self.find_BDF_according_the_device(input[2]) ##the device_number
        #now we have all the information about the dut
        self.find_topology()

    def find_cr_space(self , BDF , name_of_component):
        temp = "set pci -s" + str(BDF) + "00"
        vendor_id_pro = VendorIDProperty(self.dutComponent.resources)
        while True:
            status, vendor_ID = vendor_id_pro.get_with_Confspace()
            #status, vendor_ID = Monostate._inner.CliAgent.exec_command(temp) ##command->set pci -s BDF 00 vendorID
            if(status != 1) :##if 1 =error
                break
            print('try again, BDF not found')
        ##now we have the vendor id
        Monostate._inner.mlxDut = vendor_id_pro.is_mlx_device()
        if Monostate._inner.mlxDut: ##mellanox device
            temp = "set pci -s" + str(BDF) + "02"
            device_id = Monostate._inner.CliAgent.exec_command(temp) ##command: set pci -s BDF 02 (device id)
            flag = True
            for device in device_cr_space.keys():
                if device == device_id:
                    flag = False
                    cr_space_str = device_cr_space[device]
                    if name_of_component == "dut":
                        self.dutComponent.resources.set_CRspace_agent(crspace_agent(cr_space_str))
                        if self.check_if_dutHasSecureFw():
                            Monostate._inner.dutComponent.resources.CR_space_agent.set_read_only_flag()
                    elif name_of_component == "upstreamComponent":
                        self.upstreamComponent.resources.set_CRspace_agent(crspace_agent(cr_space_str))
                    else:##name_of_component=="downstreamcomponent
                        self.downstreamComponent.resources.set_CRspace_agent(crspace_agent(cr_space_str))

            if flag:
                print("not found this device")
        else:   #no mlx device
            if name_of_component == "dut":
                self.downstreamComponent.resources.set_CRspace_agent(crspace_agent(None))
            elif name_of_component == "upstreamComponent":
                self.upstreamComponent.resources.set_CRspace_agent(crspace_agent(None))
            else:  ##name_of_component=="downstreamcomponent
                self.downstreamComponent.resources.set_CRspace_agent(crspace_agent(None))


    def check_if_dutHasSecureFw(self):
        cr_space = self.dutComponent.resources.CR_space_agent.get_CRspace()
        temp="flint -d" + str(cr_space) + "q"
        status, output = Monostate._inner.CliAgent.exec_command(temp)
        for line in output:
            if "Security Attributes" in line:
                data = line.split(":")
                is_secure = data[1].strip()
                if 'N/A' == is_secure:
                    Monostate._inner.dutHasSecureFw = False
                    return False
        Monostate._inner.dutHasSecureFw = True
        return True


    def find_BDF_according_the_device(self,device_number):
        for num in device_name.keys():
            if num == device_number:
                name_of_device = device_name[num]
        if name_of_device == "BW":
            Monostate._inner.dutComponent.dutComponent.resources.conf_space_agent.setBdf(self.find_BW_BDF())
        elif name_of_device == "Connect_x_5":
            Monostate._inner.dutComponent.dutComponent.resources.conf_space_agent.setBdf(self.find_Connect_x_5_BDF())
        else:
            Monostate._inner.dutComponent.dutComponent.resources.conf_space_agent.setBdf(self.find_other_BDf())


    def find_BW_BDF(self):
        primery_bus = Monostate._inner.CliAgent.exec_command("mcra 0X11021c.8")  ##command:mcra 0X11021c.8
        bridge = 123 ####################ask
        function = "0"
        BDF = primery_bus+str(2*bridge)+function
        return BDF

    def find_Connect_x_5_BDF(self):
        primery_bus = Monostate._inner.CliAgent.exec_command("mcra 0X11021c.8") ####################ask
        bridge = "123" ####################ask
        function = "0"
        BDF = primery_bus+bridge+function
        return BDF

    def find_other_BDf(self):
        mst_output = Monostate._inner.CliAgent.exec_command("mst status") ####################ask
        cr_space_str = Monostate._inner.dut
        BDF = 0
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
        heder_type_property = HeaderTypeProperty(Monostate._inner.dutComponent.resources)
        heder_type = heder_type_property.get() #get the header type
        if heder_type:    ##header_type==1 ->dut is upstream
            Monostate._inner.dutIsUpstream = True
            Monostate._inner.upstreamComponent = Monostate._inner.dutComponent
            self.find_dsc_component_BDF_conf_space() #find the other side of the link
            downstream_BDF = Monostate._inner.dwonstreamComponent.resources.conf_space_agent.getBdf()
            self.find_cr_space(downstream_BDF, "downstreamComponent")
        else:
            Monostate._inner.dutIsUpstream = False
            Monostate._inner.downstreamComponent = Monostate._inner.dutComponent
            self.find_usc_component_BDF_conf_space() ###find the other side of the link
            upstream_BDF = Monostate._inner.upstreamComponent.resources.conf_space_agent.getBdf()
            self.find_cr_space(upstream_BDF, "upstreamComponent")



    def find_dsc_component_BDF_conf_space(self):
        temp = "set pci -s" + Monostate._inner.upstreamComponent.resources.conf_space_agent.getBdf() + "19h"
        secondary_bus_number = Monostate._inner.CliAgent.exec_command(temp)
        Monostate._inner.downstreamComponent.resources. set_Confspace_agent(conf_space_agent())
        #Monostate._inner.downstreamComponent.resources.conf_space_agent.init_capbilities_table()
        Monostate._inner.downstreamComponent.resources.conf_space_agent.setBdf(secondary_bus_number) ###ask !


    def find_usc_component_BDF_conf_space(self):
        downstream_BDF = Monostate._inner.dwonstreamComponent.resources.conf_space_agent.getBdf()
        temp = "readlink - f / sys / bus / pci / devices /" + str(downstream_BDF) + "19h"
        upstreanBDF = Monostate._inner.CliAgent.exec_command(temp)
        Monostate._inner.upstreamComponent.resources. set_Confspace_agent(conf_space_agent())
        #Monostate._inner.upstreamComponent.resources.conf_space_agent.init_capbilities_table()
        Monostate._inner.upstreamComponent.resources.conf_space_agent.setBdf(upstreanBDF) ###ask !


# -----------------------------------------------------------------------
# CR space agent, here until we find solution for the import problem
# -----------------------------------------------------------------------
class crspace_agent:

    def __init__(self, CRspace):
        self.Crspace = CRspace #str

    def get_CRspace(self):
        return self.Crspace

    def set_read_only_flag(self):
        self.read_only = True

    def mst_read(self,device, address, offset=0, size=32):
        """ perform mst_read for given device, address, offset and size
        :param device - expected /dev/mst/mtxxxx_pciconf0 or other that will suite OS type
        :param address - taken from crspace_db
        :param offset - taken from crspace_db
        :param size  - taken from crspace_db
        :return : value for mcra /dev/mst/mtxxxxxxxx 0x<address>.offset:size
        rtype str in hex
        """
        inf_singletone = Monostate()
        cmd = "mcra " + device + " " + str(hex(address)) + "." + str(offset) + ":" + str(size)
        (status, output) = inf_singletone.exec_agent.execute_job_and_return_returncode_and_output(cmd)
        if status:
            return None
        output = eval(output)
        # after_analysis = operator.rshift(output, offset) & (operator.lshift(1, size) - 1)
        print("mcra read: {} - result is: {} ".format(cmd,hex(output)))
        return output

    def mst_write(self,device, address, value, offset=0, size=32):
        """ perform mst_read for given device, address, offset and size
        :param device - expected /dev/mst/mtxxxx_pciconf0 or other that will suite OS type
        :param value_to_write - what to write to register
        :param address - taken from crspace_db
        :param offset - taken from crspace_db
        :param size  - taken from crspace_db
        :return : value for mcra /dev/mst/mtxxxxxxxx 0x<address>.offset:size
        rtype str in hex
        """
        inf_singletone = Monostate()
        # word = self.mst_read(device, address)
        # mask = operator.lshift((operator.lshift(1, size) - 1), offset)
        # word = (word & ~mask | ((operator.lshift(value, offset) & mask)))
        cmd = "mcra " + device + " " + str(hex(address)) + "." + str(offset) + ":" + str(size) + " " + str(hex(value))
        (status, output) = inf_singletone.exec_agent.execute_job_and_return_returncode_and_output(cmd)
        print("mcra write: {} - return status is: {} ".format(cmd,status))
        if status != 0:
            return -1
        return 0

    def return_register(self,register_to_return):
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

    def get_pcie_data(self,field_name):
        inf_singletone = Monostate()
        addr = inf_singletone.crspace_agent.return_register(field_name)
        output = self.mst_read(inf_singletone.variables.args.mstdev, addr[self.ADDRESS], addr[self.OFFSET], addr[self.SIZE])
        return output


    def set_pcie_data(self,field_name, new_val,use_default_value=0 , show_value_of_register_after_write=0,multiple_prints=0):
        inf_singletone = Monostate()
        addr = inf_singletone.crspace_agent.return_register(field_name)
        if (use_default_value == 1):
            new_val = addr[self.DEFAULT_VALUE]
        gaps_between_registers = 0
        num_of_rep = 1
        if (multiple_prints == 1):
            gaps_between_registers=addr[self.SPACES_FOT_NEXT_ELEMENT]
            num_of_rep = int(addr[self.NUMBER_OF_AVAILABLE_NEXT_ELEMENTS])
        for x in range(0,num_of_rep):
            address_with_gap = addr[self.ADDRESS]+gaps_between_registers*x
            output = self.mst_write(inf_singletone.variables.args.mstdev,address_with_gap, new_val, addr[self.OFFSET], addr[self.SIZE])
            # print("{},{},{}".format(hex(address_with_gap),addr[1],addr[2]))
            if(show_value_of_register_after_write==1):
                print("read after write: {}".format(hex(self.mst_read(inf_singletone.variables.args.mstdev,address_with_gap,addr[self.OFFSET],addr[self.SIZE]))))

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

    def getBdf(self):
        return self._bdf

    def setBdf(self, BDF):
        self._bdf = BDF

    def exe_cmd(self, cmd, print_cmd=False):
        (status, val) = self._server.CliAgent.execute_job_and_return_returncode_and_output(cmd, print_cmd=print_cmd)
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
        return bitsVal

    def read_header(self, offset, bit_loc, size):
        aligned_offset = offset & 0xffffffc  # get to the near by long word address
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, val) = self.exe_cmd(cmd, print_cmd=False)
        val = (int(val, 16) >> ((offset % 4) * 8))
        bitsVal = self.read_bits_from_reg(val, bit_loc, size)
        return bitsVal

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

    def __init__(self, ostype):
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






















