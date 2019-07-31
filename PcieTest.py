import argparse
from abc import abstractmethod
import sys
sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project')
import Monostate.Monostate as Monostate
class PcieTest:

    def __init__(self):
        self.g_args = None
        self.args = None

    def parseArgs(self):
        parser = argparse.ArgumentParser()
        #parser.add_argument("testName", help="The name of the desired test")
        parser.add_argument("dut", help="One side of the link that we want to test:BDF,CR,MTUSB")
        parser.add_argument("--serverName", type=str, help="Insert IP if you want to work on a remote server",
                            default="Local")
        #parser.add_argument("-i", help="number of iterations", default=1)
        parser.add_argument("-p", help="Port number, Insert when using cr space device",type=int)
        self.g_args, unknown = parser.parse_known_args()
        print "parseArgs"


    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def preTest(self):
        pass

    @abstractmethod
    def postTest(self):
        pass

    @abstractmethod
    def addArgs(self):
        pass

    def main(self):
        self.parseArgs()
        self.addArgs()
        self.combineArgs()
        print self.args
        server = Monostate.Monostate(self.args.dut, self.args.serverName, self.args.p)
        self.preTest()
        self.run()
        self.postTest()

