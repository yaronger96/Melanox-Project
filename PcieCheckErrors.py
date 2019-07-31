import PcieTest


class PcieCheckErrors(PcieTest.PcieTest):
    def __init__(self):
        PcieTest.PcieTest.__init__(self)
        self.l_args = None

    def addArgs(self):
        parser = PcieTest.argparse.ArgumentParser()
        parser.add_argument("--speed", help="Expected speed in gens(1,2,3,4..)", default=None, type=int)
        parser.add_argument("--width", help="Expected width (1,2,4,8,16..)", default=None, type=int)
        self.l_args, unknown = parser.parse_known_args()
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
        print "check errors"

    def postTest(self):
        print "check errors"

    def run(self):
        print "check errors"


if __name__ == '__main__':
    test = PcieCheckErrors()
    test.main()
