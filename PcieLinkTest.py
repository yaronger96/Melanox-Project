import PcieTest
import Feature.PrintSetupInfoFeature as PrintSetupInfoFeature
import Verifier.VerifierBuilder as VerifierBuilder
import Verifier.EventHendler as EventHendler
import Operation.DisableEnableOp as DisableEnableOp

class PcieLinkTest(PcieTest.PcieTest):
    def __init__(self):
        PcieTest.PcieTest.__init__(self)
        self.l_args = None
        self.builder=None

    def addArgs(self):
        parser = PcieTest.argparse.ArgumentParser()
        parser.add_argument("-i", help="Number of wanted iterations", default=1, type=int)
        parser.add_argument("--speed", help="Expected speed in gens(1,2,3,4..)", default=None, type=int)
        parser.add_argument("--width", help="Expected width (1,2,4,8,16..)", default=None, type=int)
        self.l_args, unknown = parser.parse_known_args()
        if self.l_args.i < 1:
            print"i must be 1 or greater, exiting..."
            exit(1)
        if self.l_args.speed is None:
            print "Please state expected speed, exiting.."
            exit(1)
        if self.l_args.width is None:
            print "Please state expected width, exiting.."
            exit(1)

    def combineArgs(self):
        vars(self.g_args).update(vars(self.l_args))
        self.args = self.g_args

    def preTest(self):
        print_mono = PrintSetupInfoFeature.PrintSetupInfoFeature()
        print_mono.print_feature()     
        self.builder=VerifierBuilder.VerifierBuilder(self.args.speed,self.args.width)
        self.builder.buildVerifier()
        print "build finish !!!!!!!! "
      
    def run(self):
        op = DisableEnableOp.DisableEnableOp()
        for i in range(self.args.i):
            op.execute()

    def postTest(self):
        self.builder.getVerifierComposite().eval(0) 
        print "eval  finish !!!!!!!! "
        eventHendler=EventHendler.EventHendler()
        eventHendler. printEventHandler()
        print "event hendler finish to print his table"

    


if __name__ == '__main__':
    test = PcieLinkTest()
    test.main()
