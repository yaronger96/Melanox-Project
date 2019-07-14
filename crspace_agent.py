import os
class crspace_agent:

    def __init__(self, CRspace):
        self.Crspace = CRspace #str
        self.read_only=False

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

################################