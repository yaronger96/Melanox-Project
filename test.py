import argparse
import monostate
def main():
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument("testName", help="The name of the desired test")
    parser.add_argument("dut",help="One side of the link that we want to test:BDF,CR,MTUSB")
    parser.add_argument("--serverName", type=str,help="Insert IP if you want to work on a remote server",
                        default="Local")
    parser.add_argument("-i", help="number of iterations", default=1)
    args = parser.parse_args()
    # print args.dut
    server = monostate()





if __name__=='__main__':
    main()