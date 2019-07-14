#!/usr/bin/env python
import argparse
import sys
# sys.path.insert(0, '/auto/sw_work/fwshared/c_yarong/pci_verification/student_project/agents')
import cli_agent
import Monostate

def main():
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument("testName", help="The name of the desired test")
    parser.add_argument("dut",help="One side of the link that we want to test:BDF,CR,MTUSB")
    parser.add_argument("--serverName", type=str,help="Insert IP if you want to work on a remote server",
                        default="Local")
    parser.add_argument("-i", help="number of iterations", default=1)
    args = parser.parse_args()
    print args.dut
    cli = cli_agent.CliAgentLocal("linux")
    command = "setpci -s" + " " + args.dut + " " + "00.w"
    output, err , rc = cli.exec_command(command)
    print command
    print output , err , rc





if __name__=='__main__':
    main()