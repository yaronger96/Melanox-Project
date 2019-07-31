import sys
#sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project')
import os
from crspace_db import crspace_shomron
from crspace_db import crspace_dotan
from crspace_db import crspace_galil
from crspace_db import crspace_bluefield_pcore0
from crspace_db import crspace_bluefield_pcore1
from crspace_db import crspace_negev_pcore0
from crspace_db import crspace_negev_pcore1
from crspace_db import crspace_and_nic
class crspace_agent:

    def __init__(self, CRspace, cli):
        self.Crspace = CRspace #str
        self.portNumber = None
        self.PcoreNum = None
        self.read_only = False
        self.CliAgent = cli

    def get_CRspace(self):
        return self.Crspace
    def set_read_only_flag(self):
        self.read_only = True

    def setPortNumber(self, portNum):
        self.portNumber = portNum

    def getPortNumber(self):
        return self.portNumber

    def getPcoreNum(self):
        return self.PcoreNum

    def setPcoreNum(self, pcoreNum):
        self.PcoreNum = pcoreNum

    def getModAccordingPcoreNum(self):
        if self.PcoreNum == None:
            return -1
        if self.PcoreNum == 0:
            return 20
        if self.PcoreNum == 1:
            return 30

    def builder_CRspace_access(self,regName):
        device, address, offset, size, jump_between_port = self.getDataFromCrspaceDb(regName)
        if device is 'error' and address is 'error' and offset is 'error' and size is 'error':
            print "error with get the data from CR_space"
            exit(1)
        if self.portNumber is not None:
            if self.PcoreNum is None:
                address += jump_between_port * self.portNumber
            else:
                mod = self.getModAccordingPcoreNum()
                address += jump_between_port * (self.portNumber % mod)
        return device, address, offset, size


    def mst_read(self, regName):

        """ perform mst_read for given device, address, offset and size
        :param device - expected /dev/mst/mtxxxx_pciconf0 or other that will suite OS type
        :param address - taken from crspace_db
        :param offset - taken from crspace_db
        :param size  - taken from crspace_db
        :return : value for mcra /dev/mst/mtxxxxxxxx 0x<address>.offset:size
        rtype str in hex
        """
        device, address, offset, size = self.builder_CRspace_access(regName)
        cmd = "mcra " + device + " " + str(hex(address)) + "." + str(offset) + ":" + str(size)
        (status, output) = self.CliAgent.execute_job_and_return_returncode_and_output(cmd)
        if status:
            return None
        output = eval(output)
        # after_analysis = operator.rshift(output, offset) & (operator.lshift(1, size) - 1)
        print("mcra read: {} - result is: {} ".format(cmd, hex(output)))
        return output

    def mst_write(self,regName, value):
        """ perform mst_read for given device, address, offset and size
        :param device - expected /dev/mst/mtxxxx_pciconf0 or other that will suite OS type
        :param value_to_write - what to write to register
        :param address - taken from crspace_db
        :param offset - taken from crspace_db
        :param size  - taken from crspace_db
        :return : value for mcra /dev/mst/mtxxxxxxxx 0x<address>.offset:size
        rtype str in hex
        """
        device, address, offset, size = self.builder_CRspace_access(regName)
        # word = self.mst_read(device, address)
        # mask = operator.lshift((operator.lshift(1, size) - 1), offset)
        # word = (word & ~mask | ((operator.lshift(value, offset) & mask)))

        cmd = "mcra " + device + " " + str(hex(address)) + "." + str(offset) + ":" + str(size) + " " + str(hex(value))
        (status, output) = self.CliAgent.execute_job_and_return_returncode_and_output(cmd)
        print("mcra write: {} - return status is: {} ".format(cmd,status))
        if status != 0:
            return -1
        return 0



    # def return_register(self,register_to_return):
    #     inf_singletone = Monostate()
    #     try:
    #         return_value = inf_singletone.crspace_device.REGISTERS[register_to_return]
    #     except KeyError:
    #         print "register_to_return : " + register_to_return + " Not found in device crspace map"
    #         exit(1)

    def getDataFromCrspaceDb(self, _reg_name):

        crspace_and_nic_dict = crspace_and_nic().CrSpace_dict
        device_name = None
        data_base = None
        for crspace_from_dict in crspace_and_nic_dict.keys():
            if self.Crspace == crspace_from_dict:
                device_name = crspace_and_nic_dict[crspace_from_dict]
                break
        if device_name is None:
            print ("not found device to this Cr space: {}".format(self.Crspace))
            return 'error', 'error', 'error', 'error', 'error'
        else:
            if device_name == 'crspace_shomron':
                data_base = crspace_shomron().REGISTERS
            elif device_name == 'crspace_dotan':
                data_base = crspace_dotan().REGISTERS
            elif device_name == 'crspace_galil':
                data_base = crspace_galil().REGISTERS
            elif device_name == ['crspace_bluefield_pcore0', 'crspace_bluefield_pcore1']:
                portNumber = self.getPortNumber()
                if portNumber >= 20 and portNumber <= 27:
                    data_base = crspace_bluefield_pcore0.REGISTERS
                    self.PcoreNum = 0
                elif portNumber >= 30 and portNumber <= 37:
                    data_base = crspace_bluefield_pcore1.REGISTERS
                    self.PcoreNum = 1
            elif device_name == ['crspace_negev_pcore0', 'crspace_negev_pcore1']:
                portNumber = self.getPortNumber()
                if portNumber >= 20 and portNumber <= 27:
                    data_base = crspace_negev_pcore0.REGISTERS
                    self.PcoreNum = 0
                elif portNumber >= 30 and portNumber <= 37:
                    data_base = crspace_negev_pcore1.REGISTERS
                    self.PcoreNum = 1
            for data in data_base.keys():
                if data == _reg_name:
                    address = data_base[data][0]
                    offset = data_base[data][1]
                    size = data_base[data][2]
                    jumpBetweenPort = data_base[data][3]
                    return self.Crspace, address, offset, size, jumpBetweenPort
        print ("not fount the {} in the {} data base".format(_reg_name,device_name))
        return 'error', 'error', 'error', 'error', 'error'

    ############################################################

    ADDRESS = 0
    OFFSET = 1
    SIZE = 2
    DEFAULT_VALUE = 3
    SPACES_FOT_NEXT_ELEMENT = 4
    NUMBER_OF_AVAILABLE_NEXT_ELEMENTS = 5

    # def get_pcie_data(self,field_name):
    #     inf_singletone = Monostate()
    #     addr = inf_singletone.crspace_agent.return_register(field_name)
    #     output = self.mst_read(inf_singletone.variables.args.mstdev, addr[self.ADDRESS], addr[self.OFFSET], addr[self.SIZE])
    #     return output
    #
    #
    # def set_pcie_data(self,field_name, new_val,use_default_value=0 , show_value_of_register_after_write=0,multiple_prints=0):
    #     inf_singletone = Monostate()
    #     addr = inf_singletone.crspace_agent.return_register(field_name)
    #     if (use_default_value == 1):
    #         new_val = addr[self.DEFAULT_VALUE]
    #     gaps_between_registers = 0
    #     num_of_rep = 1
    #     if (multiple_prints == 1):
    #         gaps_between_registers=addr[self.SPACES_FOT_NEXT_ELEMENT]
    #         num_of_rep = int(addr[self.NUMBER_OF_AVAILABLE_NEXT_ELEMENTS])
    #     for x in range(0,num_of_rep):
    #         address_with_gap = addr[self.ADDRESS]+gaps_between_registers*x
    #         output = self.mst_write(inf_singletone.variables.args.mstdev,address_with_gap, new_val, addr[self.OFFSET], addr[self.SIZE])
    #         # print("{},{},{}".format(hex(address_with_gap),addr[1],addr[2]))
    #         if(show_value_of_register_after_write==1):
    #             print("read after write: {}".format(hex(self.mst_read(inf_singletone.variables.args.mstdev,address_with_gap,addr[self.OFFSET],addr[self.SIZE]))))
    #
    #     return output

################################