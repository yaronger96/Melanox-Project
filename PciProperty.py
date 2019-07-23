from abc import abstractmethod

class PciProperty:
    def __init__(self, resurces):
        self.Property_resurces = resurces
        self.whichPcore = None


    def get(self):
        if self.Property_resurces.Is_CRspace_exist():
            self.get_with_CRspace()
        elif self.Property_resurces.Is_Confspace_exist():
            self.get_with_Confspace()
        else:
            self.get_with_CliAgent()


    def set(self, value):
        if self.Property_resurces.Is_CRspace_exist():
            self.set_with_CRspace(value)
        elif self.Property_resurces.Is_Confspace_exist():
            self.set_with_Confspace(value)
        else:
            self.set_with_CliAgent(value)

    @abstractmethod
    def get_with_CRspace(self):
        pass

    @abstractmethod
    def get_with_Confspace(self):
        pass

    @abstractmethod
    def get_with_CliAgent(self):
        pass

    @abstractmethod
    def set_with_CRspace(self, value):
        pass

    @abstractmethod
    def set_with_Confspace(self, value):
        pass

    @abstractmethod
    def set_with_CliAgent(self, value):
        pass

    # def getDataFromCrspaceDb(self, _reg_name):
    #     Cr_agent = self.Property_resurces.get_CRspace_agent()
    #     Crspace = Cr_agent.get_CRspace()  ##for do--> / dev / mst / mtxxxx_pciconf0
    #     device = Crspace
    #     crspace_and_nic_dict = crspace_and_nic().CrSpace_dict
    #     device_name = None
    #     for crspace_from_dict in crspace_and_nic_dict.keys():
    #         if Crspace == crspace_from_dict:
    #             device_name = crspace_and_nic_dict[crspace_from_dict]
    #             break
    #     if device_name is None:
    #         print ("not found device to this Cr space: {}".format(Crspace))
    #         return 'error', 'error', 'error', 'error'
    #     else:
    #         if device_name == 'crspace_shomron':
    #             data_base = crspace_shomron().REGISTERS
    #         elif device_name == 'crspace_dotan':
    #             data_base = crspace_dotan().REGISTERS
    #         elif device_name == 'crspace_galil':
    #             data_base = crspace_galil().REGISTERS
    #         elif device_name == ['crspace_bluefield_pcore0', 'crspace_bluefield_pcore1']:
    #             portNumber = self.Property_resurces.CR_space_agent.getPortNumber()
    #             if portNumber >= 20 and portNumber <= 27:
    #                 data_base = crspace_bluefield_pcore0.REGISTERS
    #                 self.whichPcore = 0
    #             elif portNumber >= 30 and portNumber <= 37:
    #                 data_base = crspace_bluefield_pcore1.REGISTERS
    #                 self.whichPcore = 1
    #         elif device_name == ['crspace_negev_pcore0','crspace_negev_pcore1']:
    #             portNumber = self.Property_resurces.CR_space_agent.getPortNumber()
    #             if portNumber >= 20 and portNumber <= 27:
    #                 data_base = crspace_negev_pcore0.REGISTERS
    #                 self.whichPcore = 0
    #             elif portNumber >= 30 and portNumber <= 37:
    #                 data_base = crspace_negev_pcore1.REGISTERS
    #                 self.whichPcore = 1
    #         for data in data_base.keys():
    #             if data == _reg_name:
    #                 address = data_base[data][0]
    #                 offset = data_base[data][1]
    #                 size = data_base[data][2]
    #                 return device, address, offset, size
    #     print ("not fount the {} in the {} data base".format(_reg_name,device_name))
    #     return 'error', 'error', 'error', 'error'

    # def getPcoreNum(self):
    #     return self.whichPcore

    # def getModAccordingPcoreNum(self):
    #     if self.whichPcore == None:
    #         return -1
    #     if self.whichPcore == 0:
    #         return 20
    #     if self.whichPcore == 1:
    #         return 30




